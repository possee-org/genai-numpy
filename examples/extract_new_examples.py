import os
import re
import io
import sys

# Needed for windows output capturing
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def split_log(text: str):
    parts = text.split('\nassistant\n\n')
    prompt = parts[0]
    output = parts[1]
    return prompt,output

def extract_examples(text: str):
    """
    Extracts examples from a log file, both prompt and output.
    """

    # return text

    lines = text.split('\n')
    new_lines = []
    in_examples = False

    for i, line in enumerate(lines):
        stripped_line = line.strip()

        if in_examples:
            # Check if the current line is the start of a new section or end of the text
            if i + 1 < len(lines) and lines[i + 1].strip().startswith('---') and len(lines[i + 1].strip()) == len(lines[i].strip()):
                in_examples = False
            # Check if left docstring
            elif stripped_line == '' or line.startswith('    '):
                new_lines.append(line)
            else:
                in_examples = False

        if stripped_line == "Examples" or stripped_line == "Examples:":
            if i + 1 < len(lines) and lines[i + 1].strip().startswith('---'): # and len(lines[i + 1].strip()) == len(lines[i].strip()):
                new_lines.append(line)
                in_examples = True

    return ('\n'.join(new_lines)).rstrip() + '\n'



def display_side_by_side(str1, str2, width=40, show=False):
    # Split the strings into lines
    lines1 = str1.split('\n')
    lines2 = str2.split('\n')

    # Get the maximum number of lines
    max_lines = max(len(lines1), len(lines2))

    # Pad lines to ensure both strings have the same number of lines
    padded_lines1 = lines1 + [''] * (max_lines - len(lines1))
    padded_lines2 = lines2 + [''] * (max_lines - len(lines2))

    comparison_results = []
    new_lines = []

    # Create the side-by-side display
    for i in range(max_lines):
        line1 = padded_lines1[i]
        line2 = padded_lines2[i]

        if i < len(lines1) and i < len(lines2):
            same = 'True' if line1 == line2 else 'False'
        else:
            same = 'False'

        # Save the result in the array
        comparison_results.append(same)

        new_lines.append(f'{line1:<{width}} {line2:<{width}} {same}')
    if show == True:
        print( '\n'.join(new_lines))
    return comparison_results

def count_swaps(comparison_results):
    # Initialize the count of swaps
    swap_count = 0

    # Iterate through the comparison results to count swaps
    for i in range(1, len(comparison_results)):
        if comparison_results[i] != comparison_results[i - 1]:
            swap_count += 1

    return swap_count


def process_log_files_swap(start_directory):
    results = []
    for root, dirs, files in os.walk(start_directory):
        for file in files:
            if file.endswith(".log"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    log_text = f.read()
                    prompt, output = split_log(log_text)
                    comparison_results = display_side_by_side(extract_examples(prompt),extract_examples(output),80)
                    swap_count = count_swaps(comparison_results)
                    results.append(f"{swap_count}: {file_path}\n")
    # Sorting the array based on the numeric part before the colon
    sorted_array = sorted(results, key=lambda x: int(x.split(':')[0]), reverse=True)

    with open("swap_results.txt", 'w') as result_file:
        result_file.writelines(sorted_array)
    return sorted_array

def process_paths(log_lines):
    path_components = []

    for line in log_lines:
        # Extract the path part from each line
        path = line.split(': ')[1]
        # Remove the leading '.'
        path = path.lstrip('.\\').rstrip()
        # Split the path on '\'
        components = path.split('\\')
        # Append the components to the list
        path_components.append(components)

    return path_components


# I need a function that will count the length of old array, and length of new array, and compare it to the number of equal lines.
def process_log_files_counts(start_directory):
    results = []
    for root, dirs, files in os.walk(start_directory):
        for file in files:
            if file.endswith(".log"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    log_text = f.read()
                    prompt, output = split_log(log_text)
                    prompt_examples = extract_examples(prompt)
                    output_examples = extract_examples(output)
                    comparison_results = display_side_by_side(prompt_examples,output_examples, 80)
                    swap_count = count_swaps(comparison_results)
                    # print(comparison_results)
                    false_count = comparison_results.count('False')
                    true_count = comparison_results.count('True')
                    output_len = len(output_examples.split('\n'))
                    prompt_len = len(prompt_examples.split('\n'))
                    expected_false_count = output_len - prompt_len
                    diff = expected_false_count - false_count
                    result_array = [
                        swap_count,
                        diff,
                        expected_false_count,
                        false_count,
                        true_count,
                        output_len,
                        prompt_len,
                    ]
                    results.append(f"{diff}: {result_array}: {file_path}\n")
    # Sorting the array based on the numeric part before the colon
    sorted_array = sorted(results, key=lambda x: int(x.split(':')[0]), reverse=True)

    with open("count_results.txt", 'w') as result_file:
        result_file.writelines(sorted_array)
    return sorted_array



def test_extract_examples():

    # Replace 'your_directory_path' with the actual directory path you want to start from
    # path_components = ['log', 'np_linalg']
    path_components = ['log']
    start_directory = file_path = os.path.join('.', *path_components)

    # This checks how many swaps there are lines being equal, to lines being different.
    sorted_array = process_log_files_swap(start_directory)
    log_lines = process_paths(sorted_array[0:1])

    process_log_files_counts(start_directory)
    # print(log_lines)

    logs = [
        # ['log', 'np_ma', 'np_ma_amax_70B.log'],
        # ['log', 'np_ma', 'np_ma_alltrue_70B.log'],
        # ['log', 'np_ma', 'np_ma_union1d_70B.log'],
        # ['log', 'np_linalg', 'np_linalg_svd_70B.log'],
        # ['log', 'np_linalg', 'np_linalg_eig_70B.log'],
        # ['log', 'np_linalg', 'np_linalg_inv_70B.log'],
        ['log', 'np_linalg', 'np_linalg_tensordot_70B.log'],
    ]
    # print(logs)

    logs = log_lines

    for log in logs:
        print(f'Starting {log}:')
        # Define the path components
        path_components = log

        # Construct the platform-independent file path
        file_path = os.path.join('.', *path_components)
        # Open the file and read its contents into a single string

        with open(file_path, 'r', encoding='utf-8') as file:
            log_text = file.read()

        prompt, output = split_log(log_text)

        # print("extracted_examples: PROMPT -------------------------------------------")
        # print(extract_examples(prompt))
        # print("extracted_examples: OUTPUT -------------------------------------------")
        # print(extract_examples(output))

        # print('----------------------------------------------------------')
        # print(log)
        comparison_results = display_side_by_side(extract_examples(prompt),extract_examples(output),80, show=True)
        print(comparison_results.count('False'))
        swap_count = count_swaps(comparison_results)

        print(f'{log}: Number of swaps: {swap_count}')



if __name__ == "__main__":
    test_extract_examples()



'''
I need to test if the logs always follow this pattern, of either

1. Example match is true till it hits false, then remains false.
2. There is no original examples, and so it is False always.

So it looks like I need to check for how many changes there from True to False or False to True for each log file.
That sounds completely doable, and pretty quick to do.

Time to read 1000 logs...

Wow!
'''