import re
import numpy as np
import textwrap

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



# # Function to execute the commands and get the outputs
# def execute_code(code_lines):
#     outputs = []
#     for line in code_lines:
#         command = line.strip()
#         try:
#             # Check if the command is an assignment
#             if ' = ' in command:
#                 exec(command, globals())
#                 outputs.append(None)  # No output for assignment commands
#             else:
#                 result = eval(command, globals())  # Evaluate the command if it's not an assignment
#                 outputs.append(result)
#         except Exception as e:
#             outputs.append(f"Error: {e}")
#     return outputs

# def format_output(output):
#     if isinstance(output, np.ndarray):
#         return repr(output)
#     return repr(output)

# def evaluated_code_block_old(text):
#     # Trim white space at the start of each line
#     text = '\n'.join(line.lstrip() for line in text.split('\n'))

#     # Extract the code blocks
#     code_lines = re.findall(r'>>> (.*)', text)
#     outputs = execute_code(code_lines)

#     # Create the new text with actual outputs
#     new_text_lines = []
#     output_idx = 0
#     for line in text.split('\n'):
#         if line.startswith('>>>'):
#             new_text_lines.append(line)
#             if output_idx < len(outputs):
#                 output = outputs[output_idx]
#                 output_idx += 1
#                 if output is not None:  # Skip None outputs
#                     output_str = format_output(output)
#                     # Split output into multiple lines if necessary
#                     output_lines = output_str.split('\n')
#                     new_text_lines.extend(output_lines)

#     # Add 4 spaces to the start of each line
#     new_text_lines = ['    ' + line for line in new_text_lines]

#     # Join the lines back into a single string
#     new_text = '\n'.join(new_text_lines)
#     return new_text



# # Function to execute the commands and get the outputs
# def execute_code(code_lines):
#     outputs = []
#     for line in code_lines:
#         command = line.strip()
#         try:
#             # Check if the command is an assignment
#             if ' = ' in command:
#                 exec(command, globals())
#                 outputs.append(None)  # No output for assignment commands
#             else:
#                 result = eval(command, globals())  # Evaluate the command if it's not an assignment
#                 outputs.append(result)
#         except Exception as e:
#             outputs.append(f"Error: {e}")
#     return outputs

# def format_output(output):
#     if isinstance(output, np.ndarray):
#         return repr(output)
#     return repr(output)

# def evaluated_code_block(text):
#     # Split the text into lines
#     lines = text.split('\n')
#     code_block = []
#     new_text_lines = []
#     inside_code_block = False

#     for line in lines:
#         if line.strip().startswith('>>>'):
#             inside_code_block = True
#             code_block.append(line)
#         elif inside_code_block and line.startswith('    '):
#             code_block.append(line)
#         else:
#             if inside_code_block:
#                 # Process the completed code block
#                 code_lines = [cmd[4:] for cmd in code_block if cmd.startswith('>>>')]
#                 outputs = execute_code(code_lines)
#                 output_idx = 0
#                 for cmd in code_block:
#                     new_text_lines.append(cmd)
#                     if cmd.startswith('>>>'):
#                         if output_idx < len(outputs):
#                             output = outputs[output_idx]
#                             output_idx += 1
#                             if output is not None:  # Skip None outputs
#                                 output_str = format_output(output)
#                                 output_lines = output_str.split('\n')
#                                 new_text_lines.extend(['    ' + line for line in output_lines])
#                 code_block = []
#                 inside_code_block = False
#             new_text_lines.append(line)

#     if code_block:  # Process any remaining code block
#         code_lines = [cmd[4:] for cmd in code_block if cmd.startswith('>>>')]
#         outputs = execute_code(code_lines)
#         output_idx = 0
#         for cmd in code_block:
#             new_text_lines.append(cmd)
#             if cmd.startswith('>>>'):
#                 if output_idx < len(outputs):
#                     output = outputs[output_idx]
#                     output_idx += 1
#                     if output is not None:  # Skip None outputs
#                         output_str = format_output(output)
#                         output_lines = output_str.split('\n')
#                         new_text_lines.extend(['    ' + line for line in output_lines])

#     return '\n'.join(new_text_lines)







import re
import sys
import io
from code import InteractiveInterpreter
from contextlib import redirect_stdout, redirect_stderr

def remove_python_output(text):
    # Split the text into lines
    lines = text.split('\n')
    
    # Initialize an empty list to hold the cleaned lines
    cleaned_lines = []
    
    # Variable to keep track of whether we are in a code block
    in_code_block = False
    
    # Iterate through each line
    for line in lines:
        line = line.strip()  # Remove leading and trailing whitespace

        # Check if the line starts with '>>>'
        if line.strip().startswith('>>>'):
            in_code_block = True
            cleaned_lines.append(line)
        elif line.strip().startswith('...'):
            # A continuation python block
            cleaned_lines.append(line)
        elif in_code_block and line.strip() == '':
            # End the code block on encountering a blank line
            in_code_block = False
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


# # This code does not process multi line commands. I'll remove it later
# # After I've played with the newer version.

# def process_text_block(text_block, *, shift='    '):
#     python_command_pattern = re.compile(r'^>>> (.+)')

#     lines = text_block.split('\n')
#     processed_lines = []

#     # Initialize the interpreter with current globals
#     current_globals = globals().copy()
#     interpreter = CapturingInterpreter(locals=current_globals)

#     for line in lines:
#         match = python_command_pattern.match(line)
#         processed_lines.append(shift + line)
#         if match:
#             command = match.group(1)
#             output = interpreter.run_command(command)
#             if output:
#                 for output_line in output.split('\n'):
#                     processed_lines.append(shift + output_line)

#     return '\n'.join(processed_lines)






def clean_and_process_text(text, *, rshift=4):
    cleaned_text = remove_python_output(text)
    return process_text_block(cleaned_text, rshift=4)










##### Trying to get multiline commands to work


def process_text_block(text_block, *, rshift=4):
    python_command_pattern = re.compile(r'^>>>(.*)')
    continuation_pattern = re.compile(r'^\.\.\.(.*)')

    lines = text_block.split('\n')
    processed_lines = []

    # Initialize the interpreter with current globals
    current_globals = globals().copy()
    interpreter = CapturingInterpreter(locals=current_globals)

    command = ''
    in_command = False

    for line in lines:
        match = python_command_pattern.match(line)
        if match:
            if in_command:
                output = interpreter.run_command(command.strip())
                if output:
                    for output_line in output.split('\n'):
                        processed_lines.append(' ' * rshift + output_line)
            command = match.group(1)
            in_command = True
        elif in_command:
            continuation_match = continuation_pattern.match(line)
            if continuation_match:
                command += '\n' + continuation_match.group(1)
            else:
                output = interpreter.run_command(command.strip())
                if output:
                    for output_line in output.split('\n'):
                        processed_lines.append(' ' * rshift + output_line)
                command = ''
                in_command = False
        processed_lines.append(' ' * rshift + line)

    if in_command:
        output = interpreter.run_command(command.strip())
        if output:
            for output_line in output.split('\n'):
                processed_lines.append(' ' * rshift + output_line)
        else:
            raise ValueError('Unclosed command')

    return '\n'.join(processed_lines)




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
    cleaned_text = remove_python_output(text)
    print(cleaned_text)
    print(clean_and_process_text(text))



if __name__ == '__main__':
    main()
