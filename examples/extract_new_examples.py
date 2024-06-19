import os
import re
import io
import sys
from fuzzywuzzy import fuzz
from collections import deque


# Needed for windows output capturing
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Simple function to split the log into two parts. Excellent
def split_log(text: str):
    parts = text.split('\nassistant\n\n')
    prompt = parts[0]
    output = parts[1]
    return prompt, output

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
            # Blank lines can easily be removed. Add them
            elif stripped_line == '':
                new_lines.append(line)
            # Typically lines start with 4 spaces.
            elif line.startswith('    '):
                new_lines.append(line)
            # WARNING: Sometimes AI only gets 3 on 4 space rows. This could be a problem
            elif line.startswith('   '):
                new_lines.append(line)
            # We need a reliable way to check if we left the docstring.
            # This fails if AI did not indent the docstring, which does happen.
            # AI often rambles on. Let's check if line length is greater than 100 (shouldn't happen, but could if code is long).
            # I may need a different caputre for outputs and prompts
            # Some code chunks are really long.
            elif line.strip().startswith('>>>'):
                new_lines.append(line)
            # This could be a dangerous hack.
            elif line.strip().startswith("Response generated in"):
                in_examples = False
            elif len(line) < 100:
                new_lines.append(line)
            else:
                in_examples = False

        if stripped_line == "Examples" or stripped_line == "Examples:":
            if i + 1 < len(lines) and lines[i + 1].strip().startswith('---'): # and len(lines[i + 1].strip()) == len(lines[i].strip()):
                new_lines.append(line)
                in_examples = True

    # Remove extra newlines from the right end, then make sure that one newline is added.
    return ('\n'.join(new_lines)).rstrip() + '\n'


# Keep - Does one thing, namely merges str2 into str1.
def merge_str2_into_str1(str1, str2):
    """
    The first string will remain unchanged. The second will have modifications made.
    """
    lines1 = str1.split('\n')
    lines2 = str2.split('\n')

    # Reverse the lists so we can process the lines first in first off.
    reversed1 = lines1[::-1]
    reversed2 = lines2[::-1]

    # Initialize the deque with the reversed lists
    stack1 = deque(reversed1)
    stack2 = deque(reversed2)

    max_lines = max(len(lines1), len(lines2))
    new_lines = []

    # We create a new string that matches the first and adds the non comparable items from the second.

    # This while loop must end as each option involves popping an item from a stack.
    while stack1 and stack2:
        # If they are equal, or close enough, then pop both.
        if stack1[-1].strip() == stack2[-1].strip() or fuzz.WRatio(stack1[-1].strip(), stack2[-1].strip()) > 70:
            new_line = stack1.pop()
            new_lines.append(new_line)
            stack2.pop()
        # They aren't close enough.
        # If line1 is empty (and we know not equal to the next line of line 2),
        # then add the blank line to new_lines and pop the blank line from stack 1.
        elif stack1[-1].strip() == '':
            # Note that any extra white space is preserved.
            # This could be configured differently, but I don't want to add unrelated commits.
            new_line = stack1.pop()
            new_lines.append(new_line)
        # We know that line1 is not blank.
        # We need to find the next non-blank line from stack 2.
        # If stack2 has a blank line, then pop it and start the loop again.
        elif stack2[-1].strip() == '':
            stack2.pop()
        # We now know that neither stack has a blank line on top.
        # The lines are not close enough. Keep the line from stack1, pop it, and proceed.
        else:
            new_line = stack1.pop()
            new_lines.append(new_line)

        # There is chance that this could print the entire docstring twice.
        # That will be obvious with human revision, when we delete extra examples.

    # Remove items from stack1 till it is empyt.
    # This should hopefully do nothing, but is here for a failsafe.
    # Stack 1 will be fully depleted, and be the first items on new_lines.
    while stack1:
        new_line = stack1.pop()
        new_lines.append(new_line)

    # Anything not processed from stack2 should be the new content. Add it to new lines.
    while stack2:
        new_line = stack2.pop()
        new_lines.append(new_line)

    cleaned_lines = '\n'.join(new_lines)
    return cleaned_lines



def display_side_by_side(str1, str2, width=40, show=False):
    # Split the strings into lines
    lines1 = str1.split('\n')

    ### TESTING
    # str2 = merge_str2_into_str1(str1, str2)
    lines2 = str2.split('\n')

    # Get the maximum number of lines
    max_lines = max(len(lines1), len(lines2))

    # Pad lines to ensure both strings have the same number of lines
    padded_lines1 = lines1 + [''] * (max_lines - len(lines1))
    padded_lines2 = lines2 + [''] * (max_lines - len(lines2))

    comparison_results = []
    new_lines = []
    fuzz_results = []

    # Create the side-by-side display
    for i in range(max_lines):
        line1 = padded_lines1[i]
        line2 = padded_lines2[i]

        if i < len(lines1) and i < len(lines2):
            if line1 == line2:
                same = 'True'
                fuzzscore = 100
            else:
                same = 'False'
                fuzzscore = fuzz.WRatio(line1,line2)
        else:
            same = 'False'
            fuzzscore = 0

        # Save the result in the array
        comparison_results.append(same)
        fuzz_results.append(fuzzscore)

        new_lines.append(f'{line1:<{width}} {line2:<{width}} {same} {fuzzscore}')
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
                    str1 = extract_examples(prompt)
                    str2 = extract_examples(output)
                    cleaned_out = merge_str2_into_str1(str1,str2)
                    comparison_results = display_side_by_side(str1,cleaned_out,80)
                    swap_count = count_swaps(comparison_results)
                    results.append(f"{swap_count}: {file_path}\n")
    # Sorting the array based on the numeric part before the colon
    sorted_array = sorted(results, key=lambda x: int(x.split(':')[0]), reverse=True)

    with open("swap_results.txt", 'w') as result_file:
        result_file.writelines(sorted_array)
    return sorted_array

def process_paths(log_lines, col=1):
    path_components = []

    for line in log_lines:
        # Extract the path part from each line
        path = line.split(': ')[col]
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
                    cleaned_output = merge_str2_into_str1(prompt_examples, output_examples)
                    comparison_results = display_side_by_side(prompt_examples,cleaned_output, 80)
                    swap_count = count_swaps(comparison_results)
                    # print(comparison_results)
                    false_count = comparison_results.count('False')
                    true_count = comparison_results.count('True')
                    output_len = len(cleaned_output.split('\n'))
                    prompt_len = len(prompt_examples.split('\n'))
                    expected_false_count = output_len - prompt_len
                    diff = expected_false_count - false_count
                    result_array = [
                        "swap_count" + str(swap_count),
                        "diff" + str(diff),
                        "expect" + str(expected_false_count),
                        "Falses" + str(false_count),
                        "Trues" + str(true_count),
                        "out_len" + str(output_len),
                        "prom_len" + str(prompt_len),
                        "Trues==prom_len " + str(true_count == prompt_len),
                    ]
                    results.append(f"{diff}: {result_array}: {file_path}\n")
    # Sorting the array based on the numeric part before the colon
    sorted_array = sorted(results, key=lambda x: int(x.split(':')[0]))

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
    log_lines = process_paths(sorted_array[0:45])

    sorted_array = process_log_files_counts(start_directory)
    log_lines = process_paths(sorted_array[0:1], 2)

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