import os
import re
import glob

# Define the regex pattern
pattern = re.compile(r'>>> (\w+) = .+\n\s*>>> \1')

# Function to search for the pattern in a file
def search_variable_assignment(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()

    matches = pattern.findall(content)
    return matches

# Function to search in all files in a directory and its subdirectories
def search_in_directory(directory_path):
    results = {}
    # Traverse the directory tree
    for root, dirs, files in os.walk(directory_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            matches = search_variable_assignment(file_path)
            if matches:
                results[file_path] = matches
    return results


# Specify the directory path
directory_path = 'log'

# Perform the search in the directory
directory_results = search_in_directory(directory_path)

# Print the results
if directory_results:
    print("Found variable assignments followed by variable calls in the following files:")
    for file_path, matches in directory_results.items():
        print(f"\nIn file: {file_path}")
        for match in matches:
            print(f"  Variable: {match}")
else:
    print("No matches found in any file.")

print(len(directory_results))
