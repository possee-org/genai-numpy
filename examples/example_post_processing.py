import os
import re
import os
import re
import io
import sys
from fuzzywuzzy import fuzz
# python -m pip install fuzzywuzzy
# To avoid warnings from fuzzywuzzy:
# python -m pip install python-Levenshtein
from collections import deque
import numpy as np
import textwrap
from code import InteractiveInterpreter
from contextlib import redirect_stdout, redirect_stderr


# This came from reviewtools.py, and helps format a commit message.
def format_commit_message(text, width=72, tags="[skip actions] [skip azp] [skip cirrus]"):
    """
    Format a commit message by wrapping lines and appending tags.

    Parameters
    ----------
    text : str
        The original commit message text.
    width : int, optional
        The maximum line width for wrapping paragraphs. Default is 72.
    tags : str, optional
        Tags to append to the commit message. Default is "[skip actions] [skip azp] [skip cirrus]".

    Returns
    -------
    str
        The formatted commit message with wrapped lines and appended tags.

    Notes
    -----
    The function performs the following steps:
    1. Removes newline characters from the start and end of the input text.
    2. Appends specified tags to the original message.
    3. Splits the message by newlines to process each line separately.
    4. Combines lines that are not separated by a blank line into a single paragraph.
    5. Wraps each paragraph separately to the specified width.
    6. Joins the wrapped paragraphs with newlines to form the final formatted message.
    """
    # Remove newline characters from the start and end of the message
    text = text.strip('\n')

    # Append tags to the original message
    message = text + '\n' + tags + '\n'

    # Split the message by newlines to process each line separately
    lines = message.splitlines()

    # Combine lines that are not separated by a blank line into a single paragraph
    paragraphs = []
    current_paragraph = []

    for line in lines:
        stripped_line = line.strip()
        if stripped_line == '':
            if current_paragraph:
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
            paragraphs.append('')
        elif stripped_line.startswith('-'):
            if current_paragraph:
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
            paragraphs.append(stripped_line)
        else:
            current_paragraph.append(line.strip())

    if current_paragraph:
        paragraphs.append(' '.join(current_paragraph))

    # Wrap each paragraph separately
    wrapped_paragraphs = []
    for paragraph in paragraphs:
        if paragraph.startswith('-'):
            wrapped_paragraphs.append(textwrap.fill(paragraph, width=width))
        else:
            wrapped_paragraphs.append(textwrap.fill(paragraph, width=width) if paragraph else '')

    # Join the wrapped paragraphs with newlines
    wrapped_text = '\n'.join(wrapped_paragraphs)

    return wrapped_text


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
    # This prevents a disastrous insertion of code into every file.
    if old_phrase.strip(' \n') == '':
        return r"old_phrase.strip(' \n') is empty. No replacing will happen."

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
                        # This line of code replaces `\\\\` with `\\` new_phrase.
                        # new_content = pattern.sub(new_phrase, content)
                        # We have to undo this prematurely. I hope there is a better way than this hack.
                        new_content = pattern.sub(new_phrase.replace('\\','\\\\'), content)

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

    # Don't add anything if it's just blank lines.
    if text_to_append.strip(' \n') == '':
        return docstring

    section_header = section.strip()
    # We have to deal with newlines at the start and end. Remove extras for now.
    text_to_append_lines = text_to_append.strip('\n').split('\n')

    for i, line in enumerate(lines):
        stripped_line = line.strip()

        if in_section:
            # Don't adjust the original docstring. Preserve blank lines, even if incorrect.
            # Check if the current line is the start of a new section.
            # End of docstring is dealt with later.
            if i + 1 < len(lines) and lines[i + 1].strip().startswith('---') and len(lines[i + 1].strip()) == len(lines[i].strip()):
                in_section = False
                # Remove an extra blank line before adding new content.
                if not new_lines[-1].strip():  # Remove extra blank line if exists
                    new_lines.pop()
                for j, append_line in enumerate(text_to_append_lines):
                    # If there is not a blank line before the new section, add it.
                    if j == 0 and new_lines[-1].strip() != '':
                        new_lines.append('')
                    # Now just add all the lines from the new section.
                    new_lines.append(append_line)
                # Put a blank line at the end of the added material.
                new_lines.append('')
                in_section = False

        # Don't touch anything that isn't in the corresponding section.
        new_lines.append(line)

        if stripped_line == section_header:
            if i + 1 < len(lines) and lines[i + 1].strip().startswith('---') and len(lines[i + 1].strip()) == len(lines[i].strip()):
                in_section = True
                section_found = True

    # If we are still in the section at the end of the docstring,
    # then add to that section, and make sure indentation is correct.
    # Surprising, adding a new examples section is the same code.
    if in_section or not section_found:
        # Still in section at end of docstring, or a new section will be added.
        # We need exactly one blank line between previous content and new.
        # So remove things from newlines (and make sure there is something to remove)
        while (new_lines and new_lines[-1].strip() == ''):
            new_lines.pop()
        for j, append_line in enumerate(text_to_append_lines):
            # If there is not a blank line before the new section, add it.
            if j == 0 and new_lines and new_lines[-1].strip() != '':
                new_lines.append('')
            # Now just add all the lines from the new section.
            new_lines.append(append_line)
        # Make sure the docstring ends with blank line followed by correct indentation.
        new_lines.append('')
        new_lines.append(' ' * indentation)

    return '\n'.join(new_lines)

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
    No changes are made to any lines, nor are any blank lines removed.
    Removes extra `\n` from right end, and then inserts a single `\n'.
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
            # This is the end string of each log file.
            elif line.strip().startswith("Response generated in"):
                in_examples = False
            # This could be a dangerous hack. It captures the rambling from AI.
            elif len(line) < 100:
                new_lines.append(line)
            else:
                in_examples = False

        # We will deal with the colon later. This function just captures what is there.
        if stripped_line == "Examples" or stripped_line == "Examples:":
            if i + 1 < len(lines) and lines[i + 1].strip().startswith('---'): # and len(lines[i + 1].strip()) == len(lines[i].strip()):
                new_lines.append(line)
                in_examples = True

    # Remove extra newlines from the right end, then make sure that one newline is added.
    return ('\n'.join(new_lines)).rstrip(' \n') + '\n'

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
    if cleaned_lines.strip(' \n') == '':
        return ''

    return cleaned_lines

# Removes AI generated output from string. Set skip to length of original example section.
def remove_python_output(text, *, skip=0):
    """
    Removes python output after `>>>` commands.
    Designed to be used right before `process_text_block`
    Skips checking the first `skip` lines.
    No indentation adjustments are made.
    """
    if text == '':
        return ''

    # Split the text into lines, adding one line at end.
    text = text + '\n'
    lines = text.split('\n')

    # Initialize an empty list to hold the cleaned lines
    cleaned_lines = []

    # Variable to keep track of whether we are in a code block
    in_code_block = False

    # Iterate through each line
    for i,line in enumerate(lines):
        # Don't modify lines above skip.
        if i < skip:
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
            # End the code block on encountering a blank line. The added one at the start guarantees we will leave.
            in_code_block = False
            cleaned_lines.append(line)
        elif (in_code_block and
                  # Start of sentence.
                  line.strip().startswith(tuple('ABCDEFGHIJKLMNOPQRSTUVWXYZ')) and
                  # More than just True/False.
                  len(line.strip())>12):
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
    cleaned_text = '\n'.join(cleaned_lines).strip('\n') + '\n'

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

    def add_output(output, rshift):
        for output_line in output.split('\n'):
            if output_line: # Don't add blank lines.
                processed_lines.append(' ' * rshift + output_line)


    for i, line in enumerate(lines):
        match = python_command_pattern.match(line.strip())
        if match:
            if in_command:
                output = interpreter.run_command(command.strip())
                # check skip, write output otherwise.
                if output and i >= skip:
                    add_output(output, rshift)
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
                    add_output(output, rshift)
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
            add_output(output, rshift)
        else:
            raise ValueError('Unclosed command')

    return '\n'.join(processed_lines)

# Uses the first non blank line in a multiline string to determine indentation. This is passed as rshift to process_text_block.
def find_indentation(multiline_string):
    """
    Generated by AI - Adapted by a human
    """
    # The first line of the docstring might be improperly indented.
    # So grab the first non-blank line after that.
    lines = multiline_string.splitlines()
    for line in lines[1:]:
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
    processed_text = process_text_block(cleaned_text, rshift=indent, skip=skip)
    if processed_text.strip(' \n') == '':
        return ''
    return processed_text

# Get the examples sections.
def get_prompt_and_merged_example_sections_from_file(file_path, include_output=False):
    with open(file_path, 'r', encoding='utf-8') as f:
        log_text = f.read()
    prompt, output = split_log(log_text)
    prompt = extract_examples(prompt).replace('\\','\\\\')
    output = extract_examples(output).replace('\\','\\\\')
    merged = merge_str2_into_str1(prompt, output)
    if include_output:
        return prompt, merged, output
    return prompt, merged

# Used to pull out lines of text bewteen first and last >>>, with a before and after parameter.
# AI created
def extract_quoted_section(input_string, before=0, after=0):
    lines = input_string.splitlines()
    lines = [line.strip() for line in lines] # Human added.
    start_index = None
    end_index = None

    # Find the start and end indices
    for i, line in enumerate(lines):
        if line.startswith('>>>'):
            if start_index is None:
                start_index = i
            end_index = i

    # If no such lines are found, return None
    if start_index is None or end_index is None:
        return None

    # Calculate the indices to include the before and after lines
    start_index = max(start_index - before, 0)
    end_index = min(end_index + after, len(lines) - 1)

    # Extract the lines between the calculated indices
    quoted_section = lines[start_index:end_index + 1]
    return "\n".join(quoted_section)


def get_output_examples_when_no_examples_section(output, rshift):
    # We'll grab the portions of text that have >>> in them.
    # I don't need anything after new examples.
    # AI always had any comment above within 2 lines.
    # If we pulled an extra line of code, that should get stripped later.
    out_quoted = extract_quoted_section(output, before = 2, after=0)
    if out_quoted:
        out_quoted = 'Examples\n--------\n' + out_quoted
        out_quoted_lines = out_quoted.splitlines()
        spaces = ' ' * rshift
        out_quoted_lines = [spaces + line for line in out_quoted_lines]
        return '\n'.join(out_quoted_lines)
    return ''

# Get the examples sections, but use docstring.
def get_prompt_and_merged_example_sections_from_file_and_docstring(file_path, docstring, include_output=False):
    with open(file_path, 'r', encoding='utf-8') as f:
        log_text = f.read()
    prompt, output = split_log(log_text)
    prompt_examples = extract_examples(docstring)
    output_examples = extract_examples(output).replace('\\','\\\\')

    if output_examples.strip(' \n') == '':
        # print("No examples auto-extracted from:")
        # print(file_path)
        rshift = find_indentation(docstring)
        output_examples = get_output_examples_when_no_examples_section(output, rshift)
        output_examples = output_examples.replace('\\','\\\\')
        # print(output_examples)

    merged_examples = merge_str2_into_str1(prompt_examples, output_examples)
    if include_output:
        return prompt_examples, merged_examples, output_examples
    return prompt_examples, merged_examples

# Get the log file path from the mod and func names.
def get_log_file_path(mod, func, base_dir = '.'):
    path_components = ['log',f'{mod.replace(".","_")}',f'{mod.replace(".","_")}_{func}_70B.log'] # Process all files.
    file_path = os.path.join(base_dir, *path_components)
    return file_path

# Get docstring for mod.func. Makes sure '\\' is replaced with '\\\\'
def get_docstring(mod, func):
    docstring = eval(mod + '.' + func + '.__doc__')
    return docstring.replace('\\','\\\\')

def extract_new_examples(old_string, new_string):
    min_length = min(len(old_string), len(new_string))
    for i in range(min_length):
        if old_string[i] != new_string[i]:
            return new_string[i:]
    if len(new_string) > min_length:
        return new_string[min_length:]
    return ""

# Create a list of the form [['np.linalg','det'],['np.linalg','svdvals'],...] containing all functions in a module.
def create_mod_func_list(mod):
    path_components = ['..','tools','tracking-lists','log',f"{mod.replace('.','_')}.log"]
    tracking_file_path = os.path.join('.', *path_components)
    # Linux version
    # tracking_file_path = f"../tools/tracking-lists/log/{mod.replace('.','_')}.log"
    mod_func_list = []
    with open(tracking_file_path, 'r') as file:
        for line in file:
            func = line.strip()
            mod_func_list.append([mod, func])
    return mod_func_list

def overwrite_docstring(mod, func, numpy_numpy_dir, output_append_path):
    #Create the file_path to proper examples/log spot.
    file_path = get_log_file_path(mod, func)
    # get the docstring
    docstring = get_docstring(mod, func)

    # Grab original examples section, and merged examples section.
    # prompt, merged = get_prompt_and_merged_example_sections_from_file(file_path)
    # Alternatly, use the docstring as original - worse performance?
    prompt, merged = get_prompt_and_merged_example_sections_from_file_and_docstring(file_path, docstring)

    # Clean and process the merged prompt.
    # Leave original prompt alone (hence skip)
    # The original prompt (part of merged) is needed to run blocks of dependent code.
    prompt_len = len(prompt.splitlines())
    try:
        cleaned_merged = clean_and_process_text(merged, skip=prompt_len)
        # We've generated the new examples. Strip the original prompt.
        new_examples = extract_new_examples(prompt, cleaned_merged)


        # Add new examples to appropriate spot in docstring.
        new_docstring = append_to_section(docstring, 'Examples', new_examples)

        # It would be nice to know if this succeeded... It should be longer than the original.
        # Somehow include this in the output.
        doc_increase = len(new_docstring.splitlines()) - len(docstring.splitlines())
        new_examples_len = len(new_examples.splitlines())

        # if docstring is tiny, then don't do anything.
        if len(docstring.splitlines()) < 5:
            files_replaced = 'docstring too short'
        else:
            files_replaced = search_and_replace_phrase(numpy_numpy_dir,docstring,new_docstring)
            # Strip ends from things before replacing?
            # files_replaced = search_and_replace_phrase(numpy_numpy_dir,docstring.strip(' \n'),new_docstring.strip(' \n'))
        with open(output_append_path, 'a') as file:
            file.write(f'{mod}.{func} - lines added: {doc_increase}, {new_examples_len} - file(s) changed: {files_replaced}' + '\n')
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        with open(output_append_path, 'a') as file:
            file.write(f'{mod}.{func} - lines added: NONE - check assistat generated code for issues.' + '\n')


if __name__ == "__main__":
    # The code fail with these, even with a try block.
    skip = [['np','get_include']]

    # Pick an entire module.
    mod_func_list = create_mod_func_list('np.linalg')

    # Start from a specific item (the 'np' namespace has tons)
    # mod_func_list = mod_func_list[140:]

    # Or manually select some
    # mod_func_list = [['np.linalg','svdvals'], ['np.linalg','cholesky']]

    # Path to your numpy/numpy directory. This assume you have numpy/ and genai-numpy/ repos in the same folder.
    numpy_numpy_dir_path_components = ['..','..','numpy','numpy']
    numpy_numpy_dir = os.path.join('.', *numpy_numpy_dir_path_components)
    # Path to where you want a report generated.
    output_append_path = 'reports/processed_files.txt'

    # Ensure the directory exists
    directory = os.path.dirname(output_append_path)
    os.makedirs(directory, exist_ok=True)

    # Open the file and empty it. The rest of the writes will be appends.
    with open(output_append_path, 'w') as file:
        file.write('')

    # Process all the functions in your list
    for item in mod_func_list:
        if item not in skip:
            mod, func = item
            try:
                overwrite_docstring(mod, func, numpy_numpy_dir, output_append_path)
            except Exception as e:
                print(f"An unexpected error occurred in overwrite_docstring({mod}.{func}): {e}")











