import numpy as np
import inspect
import importlib
import pkgutil
from exllamav2 import (
    ExLlamaV2,
    ExLlamaV2Config,
    ExLlamaV2Cache,
    ExLlamaV2Tokenizer,
    ExLlamaV2Cache_Q4,
)

# Function to recursively find functions with 'axis' parameter in a module and its submodules
def find_functions_with_axis(module):
    axis_functions = []

    # Inspect members of the module
    for name, member in inspect.getmembers(module):
        if inspect.isfunction(member) and 'axis' in inspect.getfullargspec(member).args:
            axis_functions.append((name, member))

    # Recursively inspect submodules
    if hasattr(module, '__path__'):
        for importer, submodule_name, ispkg in pkgutil.walk_packages(module.__path__, module.__name__ + '.'):
            try:
                submodule = importlib.import_module(submodule_name)
                axis_functions.extend(find_functions_with_axis(submodule))
            except ImportError:
                pass  # Skip modules that can't be imported

    return axis_functions

# Find all functions with an axis parameter in the numpy package
all_axis_functions = find_functions_with_axis(np)

# Extract function signatures and docstrings
prompts = []
for name, func in all_axis_functions:
    try:
        signature = inspect.formatargspec(func.__signature__, format=' positional')
    except Exception as e:
        signature = str(e)
    docstring = func.__doc__ if func.__doc__ else "No docstring available."
    prompt = f"Example usage of {name} with axis parameter: {signature}\n{docstring}"
    prompts.append(prompt)

# Load the ExLlamaV2 model
model_directory = "/shared/analyst/models/Llama-3-8B-Instruct-262k-5.0bpw-h6-exl2"
config = ExLlamaV2Config(model_directory)
config.prepare()
config.max_seq_len = 32000
model = ExLlamaV2(config)
cache = ExLlamaV2Cache_Q4(model, lazy=True, max_seq_len=config.max_seq_len)
model.load_autosplit(cache)
tokenizer = ExLlamaV2Tokenizer(config)

# Set up the generator
generator = ExLlamaV2BaseGenerator(model, cache, tokenizer)
settings = ExLlamaV2Sampler.Settings()
settings.temperature = 0.7
settings.top_k = 50
settings.top_p = 0.8
settings.token_repetition_penalty = 1.01
settings.disallow_tokens(tokenizer, [tokenizer.eos_token_id])

# Generate examples
examples = []
for prompt in prompts:
    output = generator.generate_simple(prompt, settings, max_new_tokens=512, seed=1234)
    examples.append(output)

# Postprocess the generated examples
examples = [example for example in examples if example.strip() != '']

# Stop generating examples when they become repetitive or too obvious
while True:
    new_examples = []
    for example in examples:
        if example not in new_examples:
            new_examples.append(example)
        if len(new_examples) > 10:
            break
    if len(new_examples) < 10:
        break
    examples = new_examples

# Print the generated examples
for (name, func), example in zip(all_axis_functions, examples):
    print(f"{name}:\n{example}\n")
