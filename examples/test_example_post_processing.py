from example_post_processing import *

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
    old_multiline_phrase = """
    This is the docstring
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
    new_phrase = """
    This is the docstring
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
    print(repr(old_multiline_phrase))
    print(repr(new_phrase))
    print("files_replaced:")
    print(files_replaced)

def test_get_pattern():
    #
    old_multiline_phrase = """
    This is the docstring
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
    pattern = get_pattern(old_multiline_phrase)
    # print(repr(pattern))
    return(pattern)




