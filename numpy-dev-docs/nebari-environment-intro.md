# Building a development environment on Nebari

We need an environment that can run all our projects simultaneously.
We can do this on Nebari.

- The `analyst-ragna` conda environment ensures we can run Llama 3 and Ragna.
- A new `analyst-numpy-dev` conda environment loads the needed backend (non python) packages required to build NumPy.
- A virutal environment (created by you) such as `numpy-dev` will hold the python requirements. 

All environments use Python 3.11.9, so we can stack these environments on each other to get all at the same time.
 
## Setup Conda Environments and Build NumPy

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

>    **Note:** At this point, I see the following in my terminal:
>    ```
>    (numpy-dev) (analyst-numpy-dev) bwoodruff:~/repos/numpy[main]
>    ```
>    This means I'm on branch `main`,
>    in the conda environment `analyst-numpy-dev`,
>    using the virtual environment `numpy-dev`.
>    The fact that we are stacked on top of `analyst-ragna` is not visible.

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
pip install .
```
The `pip install .` makes sure that pip installs this development build. When the above completes, let's see if the development version is installed. 
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
# 2.1.0.dev0+git20240604.24cdc31
```
We've got a development version. Yay! 

>   **_NOTE:_** This version of NumPy is installed inside your virtual environment.
>   Try leaving your virtual environment and verify that a different version of NumPy is installed.
>
>   ```
>   deactivate
>   python -c "import numpy as np; print(np.__version__)"
>   # 1.26.4
>   ```
>
>   Don't forget to reactivate your virtual environment.
>
>   ```
>   source ~/numpy-dev/bin/activate
>   ```

### Build the docs

Now build the docs. Remeber to return to the `numpy` directory. 
```
cd ~/repos/numpy
spin docs
```
>   **Note:** that `spin docs` automatically builds NumPy if it is not yet built.
>    The `--clean` argument wipes any previous NumPy build. This is sometimes needed to see docstring changes.
>   ```
>   spin docs --clean
>   ```

You can view the docs as HTML.

```
cd /repos/numpy/doc/build/html
python -m http.server
```

Then head to `https://possee.openteams.com/user/bwoodruff/proxy/8000/` (replace `bwoodruff` with your username). It's the same base URL that use for Ragna. I have it bookmarked, and just swap the 31477 to 8000. Use `Cntr+C` to terminate the server in the terminal when you're ready to move on.

### Run the codebase tests

Let's run the codebase [tests](https://numpy.org/devdocs/dev/development_environment.html#testing-builds). 

```
spin test
```

When this finishes, you'll see something like

```
46703 passed, 2291 skipped, 2786 deselected, 34 xfailed, 5 xpassed in 301.23s (0:05:01)
```

The `xfailed` and `xpassed` are designed to do this. We'll only need to run this again if we change the code base (more than just the docs). 

### Test examples in the docs

We will be updating documentation, of which there are `.rst` files and docstrings. 
Here's how we test changes to both.

```
pip install . # If you didn't do this after spin build 
python tools/refguide_check.py --rst
python tools/refguide_check.py --doctests
```

There are versions of these commands which will test specific files and functions.

>   **Note:** Currently, one of the doctests [fails on ma.power](https://github.com/numpy/numpy/commit/2059dd9e6dce61d4c52571b3865faebd8fd5ccec#commitcomment142702689). We can ignore this. 

That's all the stuff we need to check with regards to our NumPy development environment. 

## VS Code and Jupyter Notebooks

### Using VS Code 

The second to last tab at the top of the JupyterLab window is `Services`.
The last item on that tab is `Open VS Code`.
Please open VS code.
When it opened for me, I needed to reload the three environments.

```
conda activate analyst-ragna
conda activate --stack analyst-numpy-dev
source ~/numpy-dev/bin/activate

```

Now we have a working VS Code environment. You can work in this environment regularly. Remember to use the small instance if you're not doing anything that will require VRAM. You can pick a starting directory from the browser's URL. 

I'm going to open a terminal (icon in upper right corner) and test the NumPy version.

```
cd
python -c "import numpy as np; print(np.__version__)"
# 2.1.0.dev0+git20240604.24cdc31
```

### Syncronize pip packages across three environments

The stacked conda environments provide the virtual enviroment `numpy-dev` with the needed system structure. However, the pip installed resources are not shared. For example, from the terminal in VS Code try running

```
python -c "import panel as pn; print(pn.__version__)"
```

This should fail, saying `ModuleNotFoundError: No module named 'panel'`.  This package is needed for the Llama 3 panel chat. Let's resolve this. 

In VS Code, navigate to the following directory. 

```
cd ~/numpy-dev/lib/python3.11/site-packages
```

In this directory, create a new file called `conda_packages.pth`. Add these two lines to that file and save it. 

```
/home/conda/analyst/envs/analyst-numpy-dev/lib/python3.11/site-packages
/home/conda/analyst/envs/analyst-ragna/lib/python3.11/site-packages
```

When you load the `numpy-dev` virtual enviroment, each line of `conda_packages.pth` extends the `sys.path` in python, enabling access to the pip installed resources from each conda environment. After saving, we can now test that things are working with:

```
python -c "import panel as pn; print(pn.__version__)"
# 1.3.8
```

I think it's worth seeing how things are connected a bit more.  Note that `panel` is not included in the `analyst-numpy-dev` environment. We can deactivate the `numpy-dev` virtual environment, and then while in the `analyst-numpy-dev` conda environment we should get an error. 

```
deactivate # closes virtual environment
python -c "import panel as pn; print(pn.__version__)"
# ModuleNotFoundError: No module named 'panel'
```

To remove the stacked environment, we use `conda deactivate`, returning us to `analyst-ragna`.

```
conda deactivate # closes analyst-numpy-dev
python -c "import panel as pn; print(pn.__version__)"
# 1.3.8
```
### Configure Jupyter to recognize your virtual environment

Close VS Code and return to JupyterLab.

We're just about done. We have to tell Juypter that your new `numpy-dev` virtual environment is an option for starting a kernel. Make sure your virtual environment is loaded (on the stack conda environment), and then in the terminal run:

```
python -m ipykernel install --user --name numpy-dev --display-name "numpy-dev"
```

The package `ipykernel` is running from the `analyst-ragna` environment. If you encounter a "not installed" issue, then go back up and check your environments. 

You can verify that your `numpy-dev` environment is now an option for Jupyter notebook kernels by running:

```
jupyter kernelspec list
# Available kernels:
#   numpy-dev    /home/bwoodruff/.local/share/jupyter/kernels/numpy-dev
#   python3      /home/conda/analyst/a59d6f5f-1717525483-12-numpy-dev/share/jupyter/kernels/python3
```

If you mess up, or need to make changes, remember to uninstall the wrong kernel (whatever name you gave it).

```
jupyter kernelspec uninstall numpy-dev
```

Now open another tab and you should see `numpy-dev` as an option for starting a new notebook.  Start a new notebook with your new environment, and then verify the following:

```
>>> import numpy as np
>>> np.__version__
'2.1.0.dev0+git20240604.24cdc31' # may vary
>>> import panel as pn
>>> pn.__version__
'1.3.8' 
```

### Using Llama 3 and Ragna

You're ready to start using Nebari for all your work. Feel free to power down your instance, and then launch a T4 1x to test Llama 8B and Ragna. Remember to start every session by enabling the virtual environment inside a stacked conda environment. 

```
conda activate analyst-ragna
conda activate --stack analyst-numpy-dev
source ~/numpy-dev/bin/activate
```

I've tried the panel chat (Jupyter Notebook running Llama 3), an example-generator (`.py` files ran with `python name.py`), and followed the instructions to load Ragna. 

```
export PYTHONPATH=$PYTHONPATH:'/shared/analyst/ragna/'
ragna api &  # takes ~30s before it's ready
ragna ui --no-start-api  # takes ~30s before it's ready
```

All of these seem to work fine, despite the following ominous error message.

### An Ominous Error Message

Because we are using a NumPy 2.1 dev version, we'll encounter this error message: 

```
A module that was compiled using NumPy 1.x cannot be run in
NumPy 2.1.0.dev0 as it may crash. To support both 1.x and 2.x
versions of NumPy, modules must be compiled with NumPy 2.0.
Some module may need to rebuild instead e.g. with 'pybind11>=2.12'.

If you are a user of the module, the easiest solution will be to
downgrade to 'numpy<2' or try to upgrade the affected module.
We expect that some modules will need time to support NumPy 2.
```

I've seen it show up in the panel chat, and the inference example, but it didn't appear when running Ragna. I ignored the error, and things seem to work fine regardless.  This could become a bigger issue (hopefully not).

### Using Jupyter Notebooks - beware of `.ipynb_checkpoints` folders

Every time you open a file in Jupyter Lab, the autosave feature creates a `ipynb_checkpoints` folder, and a copy of what you're doing is stored there. This is great for versioning, but causes problems once you create one of these folders in your NumPy repo.  If you end up creating such folder in the NumPy repo, then you'll have to remove it. You can manually delete the directory using. 

```
rm -rf .ipynb_checkpoints/
```

I use VS Code when I want to edit a file that isn't a Jupyter notebook. This stops the issue.



## GitHub fine-grained PAT for automatic authentication

It would be nice to not have to authenticate with GitHub each time you want to push changes. 
We'll can configure a GitHub PAT on Nebari so that we can push changes our personal fork of NumPy and genai-numpy. 
Open a terminal in Jupyter Lab (not VS code).

Start by making sure you set your GitHub [username](https://docs.github.com/en/get-started/getting-started-with-git/setting-your-username-in-git?platform=linux) and [email](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-email-preferences/setting-your-commit-email-address?platform=linux#setting-your-email-address-for-every-repository-on-your-computer) on Nebari. Change `YOUR_USERNAME` and `YOUR_EMAIL` below.

```
git config --global user.name "YOUR_USERNAME"
git config --global user.email "YOUR_EMAIL"
```

We'll can create a personal access token (PAT) for this project. 
I chose to use a [fine grained PAT](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#fine-grained-personal-access-tokens), because then I can restrict access to my forks of numpy and genai-numpy.
Follow the [instructions for creating a fine-grained PAT](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token). 
All options were turned off at the start of creating the token. 

- I chose "Only select repositories" and specifically chose "bmwoodruff/numpy" and "bmwoodruff/genai-numpy" as the two repos that could be accessed. You'll want to adjust those to your username. 
- I chose to enable all 27 repository permission (probably way more than needed).
- I didn't enable any account permissions.
- After generating your token, save it somewhere temporarily. The PAT will start with `github_pat_` followed by numbers and letters. 

Let's get that token saved on Nebari so you never need to authenticate again.
First we have to tell git how you'll store your PAT.

```
git config --global credential.helper store
```

This tells git that you want to appropriately store your PAT in a plain text file in your home directory, namely `~/.git-credentials`. 

>    **Note:** This is a plain text file, so anyone with root access to the machine will be able to see this PAT. Because this is a fine-grained PAT that only has access to two repositories, I'm not worried about security issues. 

We now need to trigger an action that will cause git to ask for your username and password (our PAT). 
Pushing something to a repo will do.
I cloned `bmwoodruff/genai-numpy` to my `repos` folder, made a brach `git checkout -b testing-pat`, then pushed this branch `git push origin testing-pat`. When I pushed, I was asked for my username, and then password (I used my PAT here). 

```
bwoodruff:~/repos/genai-numpy[main] 
13:17 $ git checkout -b testing-pat
Switched to a new branch 'testing-pat'
bwoodruff:~/repos/genai-numpy[testing-pat] 
13:17 $ git push origin testing-pat
Username for 'https://github.com': bmwoodruff
Password for 'https://bmwoodruff@github.com': {paste your PAT}
```

You can view the newly created `.git-credentials` by opening it. If you haven't turned on "Show Hidden Files" yet, you'll have to do that from the "View" menu on Nebari. The file will look something like this.

```
https://bmwoodruff:{YOUR_PAT_IS_HERE}@github.com
```

That's it. You won't have to enter your username and password again while working on this machine.  Try creating another branch, push to your repo, and you'll see that authentication is automatic. At this point, I suggest delete these testing branches both on your machine, and online. 

I finished the editing of this document and pushed the changes, all from within Nebari.





