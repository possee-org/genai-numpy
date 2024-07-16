# cheatsheet_prompt.py

import numpy as np

def create_cheatsheet_prompt(module, func):
    docstring = eval(module + '.' + func + '.__doc__')
    prompt = (
        f'I will provide you with the docstring for the {func} function from the {module} module of NumPy. '
        'Create a cheatsheet that captures the essential details of the function. '
        'The cheatsheet should include the following sections: '
        'Function Description, Parameters, Returns, and Examples. '
        'Use markdown format for the cheatsheet, with headers for each section. '
        'Use the Pandas cheatsheet template style to create this.\n\n'
        'Call the function using {module}.{func}. '
        'Do not include an import statement for NumPy, '
        'as `import numpy as np` has already been called.\n\n'
        'Function Signature:\n'
        '```\n'
        '{module}.{func}()  # This should be replaced with the actual function signature\n'
        '```\n\n'
        'Function Description:\n'
        '{Function Description here}\n\n'
        'Parameters:\n'
        '- param1: Description of param1\n'
        '- param2: Description of param2\n\n'
        'Returns:\n'
        '- return1: Description of return1\n\n'
        'Examples:\n'
        '```\n'
        '{Example code here}\n'
        '```\n\n'
        'When you are finished, return the entire cheatsheet as a string. '
        'Do not provide any commentary before the returned string. '
        'If any section is not present in the docstring, mark it as "Not available." '
        '\n\n'
        f'{docstring}'
    )
    return prompt
