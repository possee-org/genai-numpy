import os
import re
import os
import re
import io
import sys
from fuzzywuzzy import fuzz
from collections import deque
import numpy as np
import textwrap
from code import InteractiveInterpreter
from contextlib import redirect_stdout, redirect_stderr

# Came from this file originally.

# Use to replace an entire docstring with a new docstring.
def search_and_replace_phrase(directory, old_phrase, new_phrase):
    """
    Replaces `old_phrase` with `new_phrase` in `directory` and all subfolders.

    Parameters
    ----------
    directory : str
        The directory to search for files containing `old_phrase`.
    old_phrase : str
        The phrase to be replaced.
    new_phrase : str
        The phrase to replace `old_phrase` with.

    Returns
    -------
    list
        A list of file paths where the replacement was made.

    Notes
    -----
    This function recursively searches through the given directory and all subfolders for files containing `old_phrase`.
    If a match is found, it replaces `old_phrase` with `new_phrase` and writes the updated content back to the file.
    Files that cannot be read as text or are not found are skipped.

    This docstring and function was generated with AI, with minimal human revision.
    """
    # Convert the old phrase to a regular expression pattern
    pattern = re.compile(re.escape(old_phrase), re.MULTILINE)

    files_replaced = []

    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    match = pattern.search(content)
                    if match:
                        # Replace the found phrase with the new phrase
                        new_content = pattern.sub(new_phrase, content)

                        # Write the updated content back to the file
                        with open(file_path, 'w', encoding='utf-8') as f_write:
                            f_write.write(new_content)

                        # print(f"Replaced text in: {file_path}")
                        files_replaced.append(file_path)
            except (UnicodeDecodeError, FileNotFoundError):
                # Skip files that can't be read as text or not found
                continue
    return files_replaced

# Use to append new examples to the end of the example section.
def append_to_section(docstring: str, section: str, text_to_append: str) -> str:
    """
    Append text to a specific section in a docstring.

    Parameters
    ----------
    docstring : str
        The original docstring.
    section : str
        The section to append the text to.
    text_to_append : str
        The text to append to the section.

    Returns
    -------
    str
        The updated docstring with the appended text.

    Raises
    ------
    ValueError
        If the specified section is not found in the docstring.

    Notes
    -----
    If the section is not found, a `ValueError` is raised. In the future, this function
    may be updated to create the section at the end of the docstring if it does not exist.

    This docstring was AI generated. The function was originally AI generated and then human adjusted.
    """
    indentation = find_indentation(docstring)
    lines = docstring.split('\n')
    new_lines = []
    in_section = False
    section_found = False

    section_header = section.strip()
    text_to_append_lines = text_to_append.lstrip('\n').rstrip('\n').split('\n')

    for i, line in enumerate(lines):
        stripped_line = line.strip()

        if in_section:
            if line == '' and new_lines[-1] =='': # Avoid double blank lines
                new_lines.pop()
            # Check if the current line is the start of a new section. End of docstring dealt with later.
            if i + 1 < len(lines) and lines[i + 1].strip().startswith('---') and len(lines[i + 1].strip()) == len(lines[i].strip()):
                in_section = False
                if not new_lines[-1].strip():  # Remove extra blank line if exists
                    new_lines.pop()
                for j, append_line in enumerate(text_to_append_lines):
                    if j == 0 and new_lines[-1].strip() != '':
                        new_lines.append('')
                    new_lines.append(append_line)
                new_lines.append('')
                in_section = False

        # Don't touch anything that isn't in the corresponding section.
        new_lines.append(line)

        if stripped_line == section_header:
            if i + 1 < len(lines) and lines[i + 1].strip().startswith('---') and len(lines[i + 1].strip()) == len(lines[i].strip()):
                in_section = True
                section_found = True

    # We are still in the section at the end of the docstring.
    if in_section or not section_found:
        # If still in section at end of docstring, append text
        if line == '' and new_lines[-1] =='': # Avoid double blank lines
            new_lines.pop()
        if not new_lines[-1].strip():  # Remove extra blank line if exists
            new_lines.pop()
        for j, append_line in enumerate(text_to_append_lines):
            if j == 0 and new_lines[-1].strip() != '':
                new_lines.append('')
            new_lines.append(append_line)
        # Make sure the docstring ends with the correct indentation pattern. We'll have a blank line.
        new_lines.append('')
        new_lines.append(' ' * indentation)

    # if not section_found:
    #     raise ValueError(f"Section '{section}' not found in the docstring.")
    #     # Update this so that it creates the section at the end of the docstring.
    #     # We'll need this for functions that don't have an Examples section.

    return '\n'.join(new_lines)

# Should be moved out of here sometime.
def test_append_to_section():
    # Example usage:
    docstring = """
        Summary of the function.

        Parameters
        ----------
        x : int
            Description of parameter `x`.
        y : float
            Description of parameter `y`.

        Examples
        --------
        First Example:

        >>> np.array([1,2])
        np.array([1,2])

        Returns
        -------
        result : bool
            Description of the return value.
    """
    section = "Examples"
    text_to_append = """


        Second (inserted) Example with lots of newlines before and after:
        Problems arise when the newlines are not blank.

        >>> np.array([1,3])
        np.array([1,3])


"""

    new_docstring = append_to_section(docstring, section, text_to_append)
    print(new_docstring)
    print(repr(new_docstring))

# Should be moved out of here sometime.
def test_search_and_replace_phrase():
    directory_to_search = "search_and_replace_test_dir"
    old_multiline_phrase = """    This is the docstring
    and I want to see what happens.
    When someone decides to add text
    to the bottom

    here is  a new line

    Examples
    --------

    first examples

    >>> code
    garbage

    second example
    >>> more code
"""
    new_phrase = """    This is the docstring
    and I want to see what happens.
    When someone decides to add text
    to the bottom

    here is  a new line

    Examples
    --------

    first examples

    >>> code
    garbage

    second example
    >>> more code

    BOOM!!!! This got added. I added it to the end so you can
    see it added multiple times.
"""
    files_replaced = search_and_replace_phrase(directory_to_search, old_multiline_phrase, new_phrase)
    print("files_replaced:")
    print(files_replaced)

# Came from extract_new_examples.py.

# Simple function to split the log into two parts.
def split_log(text: str):
    """
    Splits a text string into two parts, using '\nassistant\n\n' as the separater.
    """
    parts = text.split('\nassistant\n\n')
    prompt = parts[0]
    output = parts[1]
    return prompt, output

# Pulls out examples section from Llama3-80B log
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

# Merges str1 and str2, keeping str1 the same and appending new stuff from string 2 to end.
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


# Came from tools folder, reviewtools.py file.

# Removes AI generated output from string. Set skip to length of original example section.
def remove_python_output(text, *, skip=0):
    """
    Removes python output after `>>>` commands.
    Designed to be used right before `process_text_block`
    Skips checking the first `skip` lines.
    No indentation adjustments are made.
    """
    # Split the text into lines
    lines = text.split('\n')

    # Initialize an empty list to hold the cleaned lines
    cleaned_lines = []

    # Variable to keep track of whether we are in a code block
    in_code_block = False

    # Iterate through each line
    for i,line in enumerate(lines):
        if i<skip:
            cleaned_lines.append(line)
        # Check if the line starts with '>>>'
        elif line.strip().startswith('>>>'):
            # If there is no space above the start of a command block, then add it.
            if in_code_block == False and lines[i-1].strip() != '':
                cleaned_lines.append('')
            in_code_block = True
            cleaned_lines.append(line)
        elif line.strip().startswith('...'):
            # A continuation python block
            cleaned_lines.append(line)
        elif in_code_block and line.strip() == '':
            # End the code block on encountering a blank line.
            in_code_block = False
            cleaned_lines.append(line)
        elif in_code_block and line.strip().startswith(tuple('ABCDEFGHIJKLMNOPQRSTUVWXYZ')):
            # End the code block on encountering a sentence.
            # AI did not always do this.
            # Also add a blankline.
            in_code_block = False
            cleaned_lines.append('')
            cleaned_lines.append(line)
        elif in_code_block:
            # Skip the lines in the code block which are output
            continue
        else:
            # Add non-code block lines to the cleaned lines
            cleaned_lines.append(line)

    # Join the cleaned lines back into a single string
    cleaned_text = '\n'.join(cleaned_lines)

    # Return the cleaned text stripping extra lines off ends
    # return cleaned_text.strip()
    # Return the cleaned text preserving extra lines on ends
    return cleaned_text

# A class that allows code execution for a file. Right now uses global variables. May need to change.
class CapturingInterpreter(InteractiveInterpreter):
    def __init__(self, locals=None):
        super().__init__(locals)
        self.output = io.StringIO()

    def run_command(self, command):
        old_stdout = sys.stdout
        old_stderr = sys.stderr

        try:
            with redirect_stdout(self.output), redirect_stderr(self.output):
                # Check if the command is an expression that can be evaluated
                try:
                    result = eval(command, self.locals)
                    if result is not None:
                        if isinstance(result, (int, float, complex)):
                            print(result)  # format numbers nicely
                        else:
                            print(repr(result))  # use repr for other types
                except:
                    # If eval fails, execute the command normally
                    self.runsource(command, '<stdin>', 'single')
        except Exception as e:
            self.output.write(str(e))
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        output = self.output.getvalue()
        self.output.truncate(0)
        self.output.seek(0)
        return output.strip()

# Input merged_examples section, and then evaluates and embeds output for all new AI gen code after skip (len of orig examples section).
# Not 100% sure how it will handle errors, so needs updating.
def process_text_block(text_block, *, rshift=0, skip=0):
    """
    Goes through a block of text and runs python commands.
    Appends output directly after the python command.
    Simulates an interactive python session.
    Optional rshift command (might remove) to properly indent.
    """
    python_command_pattern = re.compile(r'^>>>(.*)')
    continuation_pattern = re.compile(r'^\.\.\.(.*)')

    lines = text_block.split('\n')
    processed_lines = []

    # Initialize the interpreter with current globals
    # Would probably be better to use some locals...
    current_globals = globals().copy()
    interpreter = CapturingInterpreter(locals=current_globals)

    command = ''
    in_command = False

    for i, line in enumerate(lines):
        match = python_command_pattern.match(line.strip())
        if match:
            if in_command:
                output = interpreter.run_command(command.strip())
                # check skip, write output otherwise.
                if output and i >= skip:
                    for output_line in output.split('\n'):
                        processed_lines.append(' ' * rshift + output_line)
            command = match.group(1)
            in_command = True
        elif in_command:
            continuation_match = continuation_pattern.match(line.strip())
            if continuation_match:
                command += '\n' + continuation_match.group(1)
            else:
                output = interpreter.run_command(command.strip())
                # check skip, write output otherwise.
                if output and i >= skip:
                    for output_line in output.split('\n'):
                        processed_lines.append(' ' * rshift + output_line)
                command = ''
                in_command = False
        # Here is where I write a line - check skip.
        if i < skip: # Preserve anything above skip.
            processed_lines.append(line)
        elif line.strip() == '': # Blank lines don't need indentation.
            processed_lines.append('')
        else:
            processed_lines.append(' ' * rshift + line.strip())

    # If in a command at end of text block, then finish the command.
    if in_command:
        output = interpreter.run_command(command.strip())
        if output:
            for output_line in output.split('\n'):
                processed_lines.append(' ' * rshift + output_line)
        else:
            raise ValueError('Unclosed command')

    return '\n'.join(processed_lines)

# Uses the first non blank line in a multiline string to determine indentation. This is passed as rshift to process_text_block.
def find_indentation(multiline_string):
    """
    Generated by AI
    """
    lines = multiline_string.splitlines()
    for line in lines:
        stripped_line = line.lstrip()
        if stripped_line:  # Check if the line is not blank
            indentation = len(line) - len(stripped_line)
            return indentation
    return 0  # Return 0 if no non-blank lines are found

# Removes python output from text and inserts generated code after skip.
def clean_and_process_text(text, *, skip=0):
    # Find indent from first nonblank.
    indent = find_indentation(text)
    cleaned_text = remove_python_output(text, skip=skip)
    return process_text_block(cleaned_text, rshift=indent, skip=skip)

# Get the examples sections.
def get_prompt_and_merged_example_sections_from_file(file_path, include_output=False):
    with open(file_path, 'r', encoding='utf-8') as f:
        log_text = f.read()
    prompt, output = split_log(log_text)
    prompt = extract_examples(prompt)
    output = extract_examples(output)
    merged = merge_str2_into_str1(prompt, output)
    if include_output:
        return prompt, merged, output
    return prompt, merged

# Get the log file path from the mod and func names.
def get_log_file_path(mod, func, base_dir = '.'):
    path_components = ['log',f'{mod.replace(".","_")}',f'{mod.replace(".","_")}_{func}_70B.log'] # Process all files.
    file_path = os.path.join(base_dir, *path_components)
    return file_path

# Get docstring for mod.func
def get_docstring(mod, func):
    docstring = eval(mod + '.' + func + '.__doc__')
    return docstring

def extract_new_examples(old_string, new_string):
    min_length = min(len(old_string), len(new_string))
    for i in range(min_length):
        if old_string[i] != new_string[i]:
            return new_string[i:]
    if len(new_string) > min_length:
        return new_string[min_length:]
    return ""



if __name__ == "__main__":
    ""
    # test_search_and_replace_phrase()
    # test_append_to_section()
    mod, func = ['np.linalg','svdvals']

    file_path = get_log_file_path(mod, func)
    prompt, merged = get_prompt_and_merged_example_sections_from_file(file_path)
    new_examples = extract_new_examples(prompt, merged)
    # print(repr(new_examples))
    # print(len(new_examples.splitlines()) > 0)
    docstring = get_docstring(mod, func)
    # print(repr(docstring))

    new_docstring = append_to_section(docstring, 'Examples', new_examples)
    # print(repr(new_docstring))
    # It would be nice to know if this succeeded... It should be longer than the original.
    # print(len(new_docstring.splitlines()) - len(docstring.splitlines()) > 0)

    numpy_numpy_dir_path_components = ['..','..','numpy','numpy']
    numpy_numpy_dir = os.path.join('.', *numpy_numpy_dir_path_components)
    # print(numpy_numpy_dir)

    files_replaced = search_and_replace_phrase(numpy_numpy_dir,docstring,new_docstring)
    print(files_replaced)











