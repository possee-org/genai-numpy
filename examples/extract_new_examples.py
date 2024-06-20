import os
import re
import io
import sys
from fuzzywuzzy import fuzz
from collections import deque
import numpy as np
from example_post_processing import *

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


