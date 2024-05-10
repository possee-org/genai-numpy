We need a way to locate functions/methods that are missing docstrings. 
The file `docstring_analysis.ipynb` recursively searches through all `.py` files
in a given directory, outputing a `.csv` that includes various information 
about each function in the files. The file can be modified to provide 
alternate information, search through different types of files (such as `.pyx` files), and more. This is a start towards locating the relevant files for which AI could help generate missing docstrings. 

- [GPT4 was used](https://chat.openai.com/share/6534b8d6-5749-4c4d-abb5-eae829edff17) to help create `docstring_analysis.ipynb`.

The file `few-shot-docstring-prompt-creator.ipynb` will create a prompt that you can pass into an LLM which includes several examples of function code and corresponding docstrings from a given file followed by code for a function that we wish to predict docstrings for. 

- [GPT4 was used](https://chat.openai.com/share/f82d5849-7224-464e-a578-d543191c8e30) to help create `few-shot-docstring-prompt-creator.ipynb`