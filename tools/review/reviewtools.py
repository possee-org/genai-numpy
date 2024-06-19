import re
import numpy as np
import textwrap
import sys
import io
from code import InteractiveInterpreter
from contextlib import redirect_stdout, redirect_stderr



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
    message = text + '\n\n' + tags + '\n'

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


def clean_and_process_text(text, *, skip=0):
    # Find indent from first nonblank.
    indent = find_indentation(text)
    cleaned_text = remove_python_output(text, skip=skip)
    return process_text_block(cleaned_text, rshift=indent, skip=skip)


def main():

    # Example usage
    text = """
        Basic correlation:

        >>> a = np.array([1, 2, 3])
        >>> v = np.array([0, 1, 0])
        >>> np.ma.correlate(a, v)
        masked_array(data=[4],
                    mask=[False],
            fill_value=999999)

        Correlation with masked elements:

        >>> a = np.ma.array([1, 2, 3], mask=[False, True, False])
        >>> v = np.ma.array([0, 1, 0])
        >>> np.ma.correlate(a, v)
        masked_array(data=[-4-],
                    mask=[ True],
            fill_value=999999,
                    dtype=int64)

        Correlation with different modes:
        >>> a = np.array([1, 2, 3])
        >>> v = np.ma.array([0, 1, 2], mask=[False, True, False])
        >>> np.ma.correlate(a, v, mode='full', propagate_mask=False)
        masked_array(data=[0, 1, 2, 3, 0],
                    mask=[False, False, False, False, False],
            fill_value=90867098999)

        >>> x = np.array([[1,2],
        ...               [3,4],
        ...               [5,6]])
        >>> x
        And then show the output
        >>> x.reshape(6,
        ...           1)
        """
    # cleaned_text = remove_python_output(text)
    # print(cleaned_text)
    print(clean_and_process_text(text, skip=0))
    prompt_text = """
        Examples
        --------
        
        Correlation with different modes:

        >>> a = np.array([1, 2, 3])
        >>> v = np.ma.array([0, 1, 2], mask=[False, True, False])
        >>> np.ma.correlate(a, v, mode='full', propagate_mask=False)
        masked_array(data=[0, 1, 2, 3, 0],
        mask=[False, False, False, False, False],
            fill_value=90867098999)
    """

    text = """
        Examples
        --------
        
        Correlation with different modes:

        >>> a = np.array([1, 2, 3])
        >>> v = np.ma.array([0, 1, 2], mask=[False, True, False])
        >>> np.ma.correlate(a, v, mode='full', propagate_mask=False)
        masked_array(data=[0, 1, 2, 3, 0],
        mask=[False, False, False, False, False],
            fill_value=90867098999)

    Words before need a blank space:
    >>> a
                                
    >>> x = np.array([[1,2],
    ...               [3,4],
    ...               [5,6]])
    >>> x
    Words after are a problem but should start with caps:
    >>> a
        
    """

    skip = len(prompt_text.splitlines())
    print(clean_and_process_text(text, skip=skip))



if __name__ == '__main__':
    main()
