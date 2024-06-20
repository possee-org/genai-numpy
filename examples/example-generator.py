import prompt_generator as my_pg

from exllamav2 import(
    ExLlamaV2,
    ExLlamaV2Config,
    ExLlamaV2Cache,
    ExLlamaV2Tokenizer,
    ExLlamaV2Cache_Q4,
)

from exllamav2.generator import (
    ExLlamaV2BaseGenerator,
    ExLlamaV2Sampler
)

import time
from datetime import datetime
from pathlib import Path

def list_model_options():
    print('Llama-3-8B-Instruct-exl2')
    print('Meta-Llama-3-70B-Instruct-4.0bpw-h6-exl2')
    return None

def function_list(module):
    # Define the file path. Assumes we are in the examples folder of genai-numpy
    file_path = '../tools/tracking-lists/log/' + module.replace('.', '_') + '.log'
    with open(file_path, 'r') as file:
        lines = file.readlines()
    filtered_lines = [line.strip() for line in lines if line.strip()]
    return filtered_lines


# def prepare_generator(model='Llama-3-8B-Instruct-exl2'):

#     return generator

def setup_generator(model_type = 'Llama-3-8B-Instruct-exl2'):
    model_directory =  '/shared/analyst/models/' + model_type

    config = ExLlamaV2Config(model_directory)
    config.prepare()
    config.max_seq_len = 32000
    model = ExLlamaV2(config)
    cache = ExLlamaV2Cache_Q4(model, lazy = True, max_seq_len=config.max_seq_len)
    model.load_autosplit(cache)
    tokenizer = ExLlamaV2Tokenizer(config)

    generator = ExLlamaV2BaseGenerator(model, cache, tokenizer)

    settings = ExLlamaV2Sampler.Settings()
    settings.temperature = 0.3
    settings.top_k = 50
    settings.top_p = 0.8
    settings.token_repetition_penalty = 1.01

    # This line was preventing the end token from being recognized.
    # settings.disallow_tokens(tokenizer, [tokenizer.eos_token_id])
    settings.set_stop_conditions = ["</s>","<|eot_id|>","<|end_of_text|>", tokenizer.eos_token_id]

    return generator, settings


def generate_and_log_examples(model_type = 'Llama-3-8B-Instruct-exl2'):
    generator, settings = setup_generator(model_type)

    system_prompt = "You are a helpful assistant working to improve the NumPy documentation. Use numpydoc style guidelines."
    modules = [
        'np.fft',
        'np.linalg',
        # 'np.polynomial',
        # 'np.polynomial.chebyshev',
        # 'np.polynomial.hermite',
        # 'np.polynomial.hermite_e',
        # 'np.polynomial.laguerre',
        # 'np.polynomial.legendre',
        # 'np.polynomial.polynomial',
        'np.random',
        # 'np.strings',
        'np.ctypeslib',
        'np.emath',
        'np.lib',
        'np.lib.scimath',
        'np.lib.stride_tricks',
        'np.lib.introspect',
        'np.lib.array_utils',
        'np.rec',
        # 'np.char', #Use strings instead
        'np.f2py', # legacy
        'np.ma', # not reliable
        # 'np',  #HUGE. Do last.
    ]

    mod_func_pairs = []
    for mod in modules:
        functions = function_list(mod)
        for func in functions:
            mod_func_pairs.append((mod,func))

    # module = 'np.strings'
    # # Define the file path. Assumes we are in the examples folder of genai-numpy
    # functions = function_list(module)
    # functions = functions[10:]


    max_new_tokens = 2000

    print("Generator Warming Up:" + f'{datetime.fromtimestamp(time.time())}')
    generator.warmup()
    print("Generator Warmed Up: " + f'{datetime.fromtimestamp(time.time())}')

    mod_func_pairs = [["np.ma", "cumsum"], ["np.ma", "prod"]]
    for module, func in mod_func_pairs:
        print(f"Starting work on {module}.{func}")
        prompt = my_pg.create_prompt(module=module, func=func, max_examples=15)
        # print(prompt)

        texts = [f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|>\n"]
        texts.append(f'<|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|>\n<|start_header_id|>assistant<|end_header_id|>')
        rendered_prompt = ''.join(texts)

        # Generate based on prompt and record how long
        time_begin = time.time()
        output = generator.generate_simple(rendered_prompt, settings, max_new_tokens, seed = 1234)
        time_end = time.time()
        time_total = time_end - time_begin

        # Define the log directory and ensure it exists
        log_dir = Path("log/" + f"{module.replace('.', '_')}")
        log_dir.mkdir(parents=True, exist_ok=True)
        with open(log_dir / f"{module.replace('.', '_')}_{func}_70B.log", 'w') as log_file:
            log_file.write(output + '\n')
            log_file.write(f"Response generated in {time_total:.2f} seconds, with a max_new_tokens = {max_new_tokens}.")

def main():
    generate_and_log_examples('Meta-Llama-3-70B-Instruct-4.0bpw-h6-exl2')


if __name__ == '__main__':
    main()
