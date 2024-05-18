# Building NumPy in GitHub Codespaces

## Quick Steps 

 Are you already familiar with codespaces? To get NumPy and the docs built, load up your fork of NumPy in codespaces and run the following commands, one by one. 

```
conda activate numpy-dev
pip install -r requirements/build_requirements.txt
spin build
pip install --pre --force-reinstall --extra-index-url https://pypi.anaconda.org/scientific-python-nightly-wheels/simple -r requirements/doc_requirements.txt
spin docs -j1
```
That should do it. You can spin up a webserver to view the docs using 

```
npm i -g http-server
http-server
```

- The command `spin build` will take 10-20 minutes the first time you build NumPy. Afterwards, it's very fast if you don't need to rebuild all the C code. 
- The command `spin docs -j1` will take about 5-10 minutes.  

## More details

Let's discuss building NumPy and the docs in codespaces with a bit more detail. 

1. We first head to GitHub and create a new codespace. From most pages you can access a new codespace using the `+` icon in the upper right. 

2. Choose the respository to be your NumPy fork, so something like
   `username/numpy`. The other settings can be left as default.
   While not neccessary, to avoid committing to `main` you can
   create a different branch first. I used `code-space-test` as 
   my branch name.

3. After your codespace loads, open a terminal within the codespace.
   You should see something like the following.
   ```
   (base) @username ➜ /workspaces/numpy (code-space-test) $
   ``` 
   We're using the `base` environment of the `code-space-test` branch.
   You'll see `main` if you didn't change the default branch. 
   Let's start by checking if `base` has the needed tools. Run each line
   below, and you should see that several tools are missing.
   ```
   python --version
   cmake --version
   meson --version
   doxygen --version
   ```

4. Load the prebuilt numpy conda environment `numpy-dev` using the command:

   ```
   conda activate numpy-dev
   ```

   Your prompt will change to

   ```
   (numpy-dev) @username ➜ /workspaces/numpy (code-space-test) $
   ``` 

   Now run the same 4 version tests from the previous step. Verify that your Python version is now 3.11.9 and all four tools are installed.

5. Let's build NumPy, which we must be done before we can build the docs.
   First install the requirements. 

   ```
   pip install -r requirements/build_requirements.txt
   ```

   Now build Numpy.

   ```
   spin build
   ```

   After 10-20 minutes this should finish. We can verify the build version as follows.

   ```
   spin python -c "import numpy as np; print(np.__version__)"
   ```

6. Now let's build the docs. First 
   [install the development versions of the doc dependencies](https://numpy.org/devdocs/dev/howto_build_docs.html#dependencies)
   (it's one long line of code).

   ```
   pip install --pre --force-reinstall --extra-index-url https://pypi.anaconda.org/scientific-python-nightly-wheels/simple -r requirements/doc_requirements.txt
   ```

   Now build the docs (takes about 5-10 minutes). The `-j1` tells your computer to use one processor and is needed to avoid a (hopefully temporary) warning message.

   ```
   spin docs -j1
   ```

   That's it. You can leave the `numpy-dev` environment by using 

   ```
   conda deactivate
   ```

7. We can view the newly built docs by 
   [enabling](https://stackoverflow.com/questions/74452866/how-preview-a-html-file-github-codespaces) 
   an `http-server` on our virtual machine. 
   Install the needed software (do this once).

   ```
   npm i -g http-server
   ```

   Now open the server. 

   ```
   http-server
   ```

   Follow the link that shows up in the lower right corner of codespaces. Then navigate to the `docs/build/html` folder. 

8. Now let's make a small change and verify that our build works. 
   Remember that we need to be in the `numpy-dev` environment for 
   our commands to work. If you deactivated that environment above,
   then reactivate it now. 

   ```
   conda activate numpy-dev
   ```

   I love linear algebra, so I opened `._linalg.py` and changed the
   documentation for `matrix_power` by adding the line `n=3` right
   after the docstrings (forcing all matrices to be raised to the 
   third power). After saving, I ran the following:

   ```
   spin python -c "import numpy as np; a=np.array([[2,0],[0,3]]); print(np.linalg.matrix_power(a,2));"
   ```

   The code above rebuilt NumPy, and the result was the matrix was raised
   to the third power, not second, as desired. Let's undo that change. 
 
   Now let's change the docs and verify our change. At the top of the
   docstrings for matrix_power, I added the words "Hello World!"
   Then I built the docs (another 5-10 minute wait). 

   ```
   spin docs -j1
   ```

   After using `http-server`, sure enough my change is visible. 



## Warning and Error messages

I have encountered the following error message near the end of the build process, on both codespaces and my local machine (though not every time).

```
WARNING: the pydata_sphinx_theme extension is not safe for parallel writing
WARNING: doing serial write
preparing documents... done
copying assets... copying static files... done
copying extra files... done
done
writing output... [100%] user/whatisnumpy
generating indices... genindex done
writing additional pages... search done
copying images... [100%] ../build/plot_directive/user/quickstart-2.png
dumping search index in English (code: en)... done
dumping object inventory... done
build finished with problems, 2 warnings.
make: *** [Makefile:144: html-build] Error 1
make: Leaving directory '/workspaces/numpy/doc'
```

Luckily, this error does not stop the docs from building. The error message is caused by the two warnings. You can still view the updated docs and verify they are correct. Using `spin docs -j1` avoids the issue.

This appears to be a recent issue that started in March this years.  A [merge](https://github.com/numpy/numpy/pull/26125) was made that fixes the CI build, which uses `make` instead of `spin`. I'll document [here](https://github.com/possee-org/genai-numpy/issues/20) how I used AI to identify the issue and create a PR. 

