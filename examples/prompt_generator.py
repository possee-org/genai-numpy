import numpy as np

def create_prompt(module, func,max_examples=15):
    docstring = eval(module + '.' + func + '.__doc__')
    prompt = (''
        f'I will provide you with the docstring for the {func} function. '
        'Examine the examples and decide if adding an example would be useful. '
        'If the current examples are sufficient, then state so. '
        'Otherwise create one example to add to the bottom of the docstring. '
        'Add the example to the bottom of the docstring. '
        f'Call the function using {module}.{func}. '
        'Do not include an import statement for numpy, '
        'as `import numpy as np` has already been called.'
        '\n\n'
        'For each example you create, include a header. '
        'The header should be written as regular text on a single line '
        'without any newline characters and end with a colon. '
        'Do not include "Example #:" in the header. '
        'The example code should start with the >>> prompt. '
        'Include a blank line between the header and the example code. '
        '\n\n'
        'Continue the process until you decide no more examples are needed '
        f'or you have created {max_examples} examples. '
        '\n\n'
        'When you are finished, return the entire examples section '
        'of the docstring as a string. '
        'Do not provide any commentary before the returned string. '
        '\n\n'
        'After you have returned the string, '
        'explain why you decided to add each example '
        'and then explain why you stopped.'
        '\n\n'
        f'{docstring}'
    )
    return prompt

# def main():
#     print(create_prompt(module='np.linalg', func='svd', max_examples=15))

# if __name__ == '__main__':
#     main()