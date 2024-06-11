# Quick commands

These are commands I use on a regular basis.

## Setting up environments on Nebari

This is needed to use Llama 3 or Ragna with the development version of Numpy. If you want the most recent version of docstrings, you'll need this.
```
conda activate analyst-ragna
conda activate --stack analyst-numpy-dev
source ~/numpy-dev/bin/activate
```
Or, more quickly, just combine them together on one line using `&&`.
```
conda activate analyst-ragna && conda activate --stack analyst-numpy-dev && source ~/numpy-dev/bin/activate
```

If I don't need Llama 3 or Ragna, then I run:
```
conda activate analyst-numpy-dev && source ~/numpy-dev/bin/activate
```

## Building Numpy and Docs

Start by making sure that you are in the `numpy` directory.  For me, that's `cd ~/repos/numpy`.  When I make a change to the code base,
then I use this sequence of commands.

This is what I use for testing documentation changes.
```
spin build --clean
python -m pip install .
rm -rf doc/source/reference/generated
spin docs --clean
python tools/refguide_check.py --rst
python tools/refguide_check.py --doctests
```

The last command above may fail on `ma.power`. Ignore that.

Again, you can chain them all together with `&&` and then do something else productive while this runs in a terminal. Or create a shell script and use that.

```
spin build --clean && python -m pip install . && rm -rf doc/source/reference/generated && spin docs --clean && python tools/refguide_check.py --rst && python tools/refguide_check.py --doctests
```

When I change the code base, I add a few more lines.

```
python tools/linter.py
spin build --clean
python -m pip install .
spin test -m full -j auto
rm -rf doc/source/reference/generated
spin docs --clean
python tools/refguide_check.py --rst
python tools/refguide_check.py --doctests
```
## Git and GitHub

Here's the commands I find myself using the most.
```
git checkout main
git pull upstream main --tags
git submodule update --init
git checkout -b my-branch-name

git checkout my-branch-name
git diff
git status
git add .
git status
git commit
git push origin my-branch-name
```