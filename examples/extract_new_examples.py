import os
import re
import io
import sys
from fuzzywuzzy import fuzz
from collections import deque
import numpy as np


# Needed for windows output capturing
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Workflow:
# Read in log file.
# Split into prompt and output.
# Merge output into prompt (preserving prompt)  merge_str2_into_str1
# Find indentation length from prompt.
# Find line on which output starts.
# Run every line of code in the cleaned example.
#    For lines in the original prompt, leave them there.
#    For new lines, remove generated output and insert proper output.
#    Make sure that there is a blank space between any text and code. This could get tricky for some.
# Locate correct file in numpy repo, and replace original docstring text with new text.
# Loop over the entire codebase (maybe do a module at a time)
# Commit changes to a branch and push.
# Manually go through and delete examples that are extra or bogus. Commit over that branch.



# This should be used to capture the indentation from the original docstring.
# It will be used to indent properly the cleaned_output.
def indent_amount(text):
    # Needs to capture an error if the text is empty, or return zero.
    lines = text.split('\n')
    first_line = lines[0]
    return len(first_line) - len(first_line.lstrip(' '))

# Simple function to split the log into two parts. Excellent
def split_log(text: str):
    """
    Splits a text string into two parts, using '\nassistant\n\n' as the separater.
    """
    parts = text.split('\nassistant\n\n')
    prompt = parts[0]
    output = parts[1]
    return prompt, output

def extract_examples(text: str):
    """
    Extracts examples from a log file, either prompt or output.
    Use an arbitrary 100 line length to determine if you've left docstring.
    Removes extra `\n` from right end, and then inserts a single `\n\'.
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
    The first string will remain unchanged.
    Both strings are first split into lines.
    The second string's same-ish lines are tossed.
    Any extra lines from the second string are then added to the end.
    Returns a string that retains all of str1 with str2's new content added to the bottom.
    Uses fuzzywuzzy WRatio > 65 to determine if same.
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
        # Close enough (WRatio > 65) was tested on the data. The lowest good match was 66. All but 1 of 829 were fine with >70.
        if stack1[-1].strip() == stack2[-1].strip() or fuzz.WRatio(stack1[-1].strip(), stack2[-1].strip()) > 65:
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



def display_side_by_side(str1, str2, width=80, show=False):
    """
    Used to compare two strings, side-by-side, for testing.
    The strings are split into lines, and then the lines are compared.
    Two extra columns are added.
    The first shows if the strings are equal.
    The second shows the fuzzywuzzy WRatio score (a 100 is inserted if equal).
    Returns the comparison_ratio list.
    Will print the side-by-side comparison if show=True.

    Could use some cleaning up, so that side-by-side is part of output.
    """
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

        # Save the result in the list
        comparison_results.append(same)
        fuzz_results.append(fuzzscore)

        new_lines.append(f'{line1:<{width}} {line2:<{width}} {same} {fuzzscore}')
    if show == True:
        print( '\n'.join(new_lines))
    return comparison_results

def count_swaps(comparison_results):
    """
    Counts how many times the values in an ordered list change.
    Used for testing the other functions.
    """
    # Initialize the count of swaps
    swap_count = 0

    # Iterate through the comparison results to count swaps
    for i in range(1, len(comparison_results)):
        if comparison_results[i] != comparison_results[i - 1]:
            swap_count += 1

    return swap_count


def process_log_files_swap(start_directory, out_file = 'swap_results.txt'):
    """
    Used to recursively test other functions on all log files from a start_directory.
    Opens each log file, splits into prompt and output, merges output into prompt,
    then builds comparison_results list (counting swaps).
    Calculates swap_count and then adds `swap_count: file_path` to a list.
    Sorts this list (largests counts first).
    Writes the list to `out_file` and returns the list.

    Colons, so `:`, are use in further processing to separate the output.

    Could definely use some cleaning up, but it was just used to help test.
    """
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
    # Sorting the list based on the numeric part before the colon
    sorted_list = sorted(results, key=lambda x: int(x.split(':')[0]), reverse=True)

    with open(out_file, 'w', encoding='utf-8') as result_file:
        result_file.writelines(sorted_list)
    return sorted_list

def process_paths(lines, col=1):
    """
    Used for testing, which I did on a Windows machine.
    Using `:`, splits a list returned from `process_log_files_swap` or
    `process_log_files_counts`. The column `col` parameter selects
    the column which contains file_paths, after spliting on `:`
    Return a list with each entry a list of path components.
    """
    path_components = []

    for line in lines:
        # Extract the path part from each line
        path = line.split(':')[col]
        path = path.strip()
        # Remove the leading '.'
        path = path.strip().lstrip('.\\').lstrip('./')
        # Split the path using the OS-specific separator
        components = path.split(os.path.sep)
        # Append the components to the list
        path_components.append(components)

    return path_components


def process_log_files_counts(start_directory, out_file = 'count_results_new.txt'):
    """
    Used to recursively test other functions on all log files from a start_directory.
    Opens each log file, splits into prompt and output, merges output into prompt,
    then builds comparison_results list (counting swaps).
    Calculates swap_count and a variety of other metrics.
    Currently those metrics have to be hard coded, rather than selected from the parameters.
    Pick one metric to put before first `:` which is used to sort.
    Other features are in an list, followed by `:`.
    File_path is then put in last column.
    Writes the list to `out_file` and returns the list.

    Colons, so `:`, are use in further processing to separate the output.

    Could definely use some cleaning up, but it was just used to help test.
    """
    results = []
    increase_in_out = []
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
                    output_len = len(output_examples.split('\n'))
                    clean_output_len = len(cleaned_output.split('\n'))
                    prompt_len = len(prompt_examples.split('\n'))
                    expected_false_count = clean_output_len - prompt_len
                    diff = expected_false_count - false_count
                    diff_out = clean_output_len - output_len
                    result_list = [
                        # "swap_count" + str(swap_count),
                        # "diff" + str(diff),
                        # "expect" + str(expected_false_count),
                        # "Falses" + str(false_count),
                        # "Trues" + str(true_count),
                        "out_len" + str(output_len),
                        "clean_len" + str(output_len),
                        # "prom_len" + str(prompt_len),
                        # "Trues==prom_len " + str(true_count == prompt_len),
                    ]
                    results.append(f"{diff_out}: {result_list}: {file_path}\n")
                    increase_in_out.append(len(cleaned_output.split('\n')) - len(output_examples.split('\n')))
    # Sorting the list based on the numeric part before the colon
    # sorted_list = sorted(results, key=lambda x: int(x.split(':')[0]), reverse=True)
    sorted_list = sorted(results, key=lambda x: int(x.split(':')[0]))


    total_count = len(increase_in_out)
    unique_values, counts = np.unique(np.asarray(increase_in_out), return_counts=True)
    summary = {
        'Total Count': total_count,
        'Unique Values': len(unique_values),
        'Value Counts': dict(zip(unique_values, counts))
    }

    with open(out_file, 'w') as result_file:
        result_file.writelines(sorted_list)
        result_file.write(str(sorted(increase_in_out, reverse=True))+"\n")
        result_file.write(str(summary))
    return sorted_list



def test_extract_examples():
    """
    This is the main function where I did my testing.
    It serves no purpose outside of this file.
    """

    # Replace 'your_directory_path' with the actual directory path you want to start from
    # path_components = ['log', 'np_linalg']
    path_components = ['log'] # Process all files.

    start_directory = file_path = os.path.join('.', *path_components)

    # This checks and writes to file how many swaps there are lines being equal, to lines being different.
    sorted_list = process_log_files_swap(start_directory, 'swap_results.txt')
    # Optional: Keep the top few to view in termainal.
    log_lines = process_paths(sorted_list[0:45])

    # This checks and writes to file various metrics.
    sorted_list = process_log_files_counts(start_directory, 'count_results.txt')
    # Optional: Keep the top few to view in termainal.
    log_lines = process_paths(sorted_list[0:4], 2)

    # print(log_lines)

    # Hand pick in a particular log(s) you wish to view side-by-side

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

    # Overrides the hand-picked choices, using lists from larger runs.
    logs = log_lines

    for log in logs:
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
        prompt_examples = extract_examples(prompt)
        output_examples = extract_examples(output)

        print(f'Starting {log}:')
        print(f'------------------------------------------ Before merging -----------------------------------------')
        comparison_results = display_side_by_side(prompt_examples,output_examples,80, show=True)
        print(comparison_results.count('False'))
        swap_count = count_swaps(comparison_results)
        print(f'{log}: Number of swaps: {swap_count}')
        print(f'------------------------------------------ After merging -----------------------------------------')
        cleaned_output_examples = merge_str2_into_str1(prompt_examples,output_examples)
        display_side_by_side(prompt_examples,cleaned_output_examples,80, show=True)




if __name__ == "__main__":
    test_extract_examples()


