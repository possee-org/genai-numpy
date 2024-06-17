import os
import re

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
            # Check if the current line is the start of a new section or end of the docstring
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

    if in_section:
        # If still in section at end of docstring, append text
        if line == '' and new_lines[-1] =='': # Avoid double blank lines
            new_lines.pop()
        if not new_lines[-1].strip():  # Remove extra blank line if exists
            new_lines.pop()
        for j, append_line in enumerate(text_to_append_lines):
            if j == 0 and new_lines[-1].strip() != '': 
                new_lines.append('')
            new_lines.append(append_line)
        new_lines.append('')

    if not section_found:
        raise ValueError(f"Section '{section}' not found in the docstring.")
        # Update this so that it creates the section at the end of the docstring.
        # We'll need this for functions that don't have an Examples section.

    return '\n'.join(new_lines)




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

if __name__ == "__main__":
    test_search_and_replace_phrase()
    test_append_to_section()