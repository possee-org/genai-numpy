# Building a development environment on Nebari

We need an environment that can run all our projects simultaneously.
We can do this on Nebari.

- The `analyst-ragna` conda environment ensures we can run Llama 3 and Ragna.
- A new `analyst-numpy-dev` conda environment loads the needed backend (non python) packages required to build NumPy.
- A virutal environment (created by you) such as `numpy-dev` will hold the python requirements. 

All environments use Python 3.11.9, so we can stack these environments on each other to get all at the same time.
 
## Walkthrough

The setup process below does not require a high powered machine. 
When you are building code and working with NumPy, use the small instance to minimize costs.
Save the T4 1x and T4 4x for when you are actually using Llama 3 and/or Ragna. 
Otherwise, feel free to use a small instance to do regular coding.
You won't need to use codespaces anymore, and by the time you're done with this intro, you'll be using VS code via Nebari.

### Launch a small instance

Launch a small instance on [Nebari](https://possee.openteams.com/hub/home) via JupyterLab.

### Activate stacked conda environments

Open a terminal and [activate both environments](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) with the following two commands:

```
conda activate analyst-ragna
conda activate --stack analyst-numpy-dev
```

This loads `analyst-ragna` and then on top of that loads `analylst-numpy-dev`.
We can now work with both environments.

### Create a virtual environment

We'll need a virtual environment on top of these conda environments in which to build NumPy.
I'll create a `numpy-dev` virtual environment in my base directory. 
```
python -m venv ~/numpy-dev
```
To activate that environment, use:
```
source ~/numpy-dev/bin/activate
```

### Clone your fork of NumPy.
Use git to clone your fork of NumPy.
I'll follow the instructions on [numpy.org](https://numpy.org/devdocs/dev/index.html). 
I prefer to not have numpy on the base directory, so I first made a `repos` folder.
Feel free to put numpy in another spot.
Here are the commands I used.
```
cd
mkdir repos
cd repos
# Remember change the next line to use your username
git clone --recurse-submodules https://github.com/bmwoodruff/numpy.git
cd numpy
git remote add upstream https://github.com/numpy/numpy.git
git checkout main
git pull upstream main --tags
git submodule update --init
```

>   **Note:** At this point, I see the following in my terminal:
    ```
    (numpy-dev) (analyst-numpy-dev) bwoodruff:~/repos/numpy[main]
    ```
    This means I'm on branch `main`,
    in the conda environment `analyst-numpy-dev`,
    using the virtual environment `numpy-dev`.
    The fact that we are stacked on top of `analyst-ragna` is not visible.

### Install NumPy requirements in your virtual environment

We now install the requirements for building NumPy, testing numpy, and [building the docs](https://numpy.org/devdocs/dev/howto_build_docs.html#dependencies). 
```
pip install -r requirements/build_requirements.txt
pip install -r requirements/test_requirements.txt
pip install --pre --force-reinstall --extra-index-url https://pypi.anaconda.org/scientific-python-nightly-wheels/simple -r requirements/doc_requirements.txt
```
>   **Note:** pip installs these in the `numpy-dev` virtual environment. 

### Build NumPy and verify the version

We now build NumPy.
```
spin build
```
When that completes, let's see if the development version is installed. 
```
python -c "import numpy as np; print(np.__version__)"
```
You'll get an error message:
```
ImportError: cannot import name 'version' from partially initialized module 'numpy' (most likely due to a circular import)
```
The problem is that we're in the NumPy base directory. Head back to your base directory and try the same. 
```
cd
python -c "import numpy as np; print(np.__version__)"
# 2.1.0.dev0+git20240531.da5a779
```
We've got a development version. Yay! 

>   **_NOTE:_** This version of NumPy is installed inside your virtual environment.
    Try leaving your virtual environment and verify that a different version of NumPy is installed.
>
>   ```
    deactivate
    python -c "import numpy as np; print(np.__version__)"
    # 1.26.4
    ```
>
>   Don't forget to reactivate your virtual environment.
>
>    ```
    source numpy-dev/bin/activate
    ```

### Build the docs

Now build the docs. Remeber to return to the `numpy` directory. 
```
cd ~/repos/numpy
spin docs
```
>   **Note:** that `spin docs` automatically builds NumPy if it is not yet built.
    The `--clean` argument wipes any previous NumPy build. This is sometimes needed to see docstring changes.
    ```
    spin docs --clean
    ```

### Run the codebase tests   

Now let's run the [tests](https://numpy.org/devdocs/dev/development_environment.html#testing-builds) on the codebase. 
```
spin test
```
When this finishes, you'll see something like
```
46703 passed, 2291 skipped, 2786 deselected, 34 xfailed, 5 xpassed in 301.23s (0:05:01)
```
The `xfailed` and `xpassed` are designed to do this. We won't be changing the codebase much, so we may not need to run this test again. 

### Test the docstrings

We will be updating documentation. 
We test changes to an `.rst` file.

```
python tools/refguide_check.py --rst
```
We can also test changes to any docstrings.

```
python tools/refguide_check.py --doctests
```

>   **Note:** Currently, one of the doctests [fails on ma.power](https://github.com/numpy/numpy/commit/2059dd9e6dce61d4c52571b3865faebd8fd5ccec#commitcomment-142702689). We can ignore this. 

That's all the stuff we need to check with regards to our NumPy development environment. We'll need to configure a GitHub PAT on the machine so that you can push changes to your fork, but for now you can work on Nebari while doing things. 

## Using VS Code 

The second to last tab at the top is `Services`.
The last item on that tab is `Open VS Code`.
When VS code opened for me, I needed to reload the three environments.
```
conda activate analyst-ragna
conda activate --stack analyst-numpy-dev
source ~/numpy-dev/bin/activate
```
Now I have a working VS Code environment.
```
cd ~
python -c "import numpy as np; print(np.__version__)"
# 2.1.0.dev0+git20240531.da5a779
```
And we can work as normal. You can run python files just fine in this environment.

## Using Jupyter Notebooks (coming soon)

Close the VS Code window to return to JupyterLab.  

UGH.... MORE TO BE ADDED.  I still have to figure out configuring Jupyter for a virtual environment on top of two stacked conda environments.  Hopefully we'll soon have a simple button click inside Juypter files that lets you run this. More coming soon.

