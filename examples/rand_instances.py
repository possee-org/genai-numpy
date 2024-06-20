import os
import re

def find_word_in_files(word, root_dir):
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                    lines = file.readlines()
                    for i,line in enumerate(lines):
                        stripped_line = line.strip()
                        if stripped_line.startswith('>>>') and word in stripped_line:
                            print(f'Found in {filepath}:')
                            print(stripped_line)
                            # Print the next two lines if they exist
                            if i + 1 < len(lines):
                                print(lines[i + 1].strip())
                            if i + 2 < len(lines):
                                print(lines[i + 2].strip())
                            print('---')
            except Exception as e:
                print(f'Could not read file: {filepath}. Error: {e}')

find_word_in_files('rand', 'log')

