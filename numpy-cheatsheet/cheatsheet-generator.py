import sys
import os

# Add the current directory to the system path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import cheatsheet_prompt as my_pg
from exllamav2 import (
    ExLlamaV2,
    ExLlamaV2Config,
    ExLlamaV2Cache_Q4,
    ExLlamaV2Tokenizer
)
from exllamav2.generator import (
    ExLlamaV2BaseGenerator,
    ExLlamaV2Sampler
)
import time
from datetime import datetime
import nbformat as nbf

def create_jupyter_notebook(module, functions, output_path):
    # Initialize the notebook
    nb = nbf.v4.new_notebook()
    nb.cells.append(nbf.v4.new_markdown_cell(f"# NumPy Cheatsheet for {module}"))

    # Initialize model and cache
    model_directory = "/shared/analyst/models/Meta-Llama-3-70B-Instruct-4.0bpw-h6-exl2"
    config = ExLlamaV2Config(model_directory)
    config.prepare()
    config.max_seq_len = 4000
    model = ExLlamaV2(config)
    cache = ExLlamaV2Cache_Q4(model, lazy=True, max_seq_len=config.max_seq_len)
    model.load_autosplit(cache)

    print("Loading Tokenizer")
    print(datetime.fromtimestamp(time.time()))
    tokenizer = ExLlamaV2Tokenizer(config)

    print("Loaded Tokenizer")
    print(datetime.fromtimestamp(time.time()))

    # Initialize generator
    generator = ExLlamaV2BaseGenerator(model, cache, tokenizer)

    print("Initialized generator")
    print(datetime.fromtimestamp(time.time()))

    # Generator settings
    settings = ExLlamaV2Sampler.Settings()
    settings.temperature = 0.85
    settings.top_k = 50
    settings.top_p = 0.8
    settings.token_repetition_penalty = 1.01
    settings.disallow_tokens(tokenizer, [tokenizer.eos_token_id])

    system_prompt = "You are a helpful assistant working to improve the NumPy documentation. Use numpydoc style guidelines."

    for func in functions:
        prompt = my_pg.create_cheatsheet_prompt(module, func)
        texts = [f"system\n\n{system_prompt}\n"]
        texts.append(f'user\n\n{prompt}\nassistant')
        rendered_prompt = ''.join(texts)

        print('-------------------------------------------------------------')
        print(rendered_prompt)

        max_new_tokens = 2000

        print("generator.warmup()")
        print(datetime.fromtimestamp(time.time()))
        generator.warmup()
        time_begin = time.time()

        print("output = generator.generate_simple(rendered_prompt, settings, max_new_tokens, seed = 1234)")
        print(datetime.fromtimestamp(time.time()))
        output = generator.generate_simple(rendered_prompt, settings, max_new_tokens, seed=1234)

        time_end = time.time()
        time_total = time_end - time_begin

        print(output)
        print()
        print(f"Response generated in {time_total:.2f} seconds, {max_new_tokens} tokens, {max_new_tokens / time_total:.2f} tokens/second")

        # Add the generated content to the notebook
        nb.cells.append(nbf.v4.new_markdown_cell(f"## {func} Function"))
        nb.cells.append(nbf.v4.new_code_cell(output))

    # Save the notebook
    with open(output_path, 'w') as f:
        nbf.write(nb, f)

# Example usage
module = 'np.linalg'
functions = ['svd', 'det', 'eig', 'lstsq']
output_path = 'numpy_cheatsheet.ipynb'

create_jupyter_notebook(module, functions, output_path)
