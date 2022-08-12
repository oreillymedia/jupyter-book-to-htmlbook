# Jupyter Book to HTMLBook

Takes a Jupyter Book (in HTML) and turns it into an HTMLBook-compliant project.

Supposes that you're in a book repo and that the output of the jupyter book script 
is in a _./html_ directory. You can change this default in 
*jupyter_book_to_htmlbook/jupyter_book_to_htmlbook.py*.

## Usage

**IMPORTANT**: We are not currently providing configuration options for the "source" directory (i.e., where the output of `jupyter book` lives) and the "build" directories -- those must be _html/_ and _build/_ directories inside the root of your Atlas repository at the present writing. 

For usage you have two options:

1. Include the *jupyter_book_to_htmlbook/* directory inside your Atlas repo and run `python3 jupyter_book_to_htmlbook/jupyter_book_to_htmlbook.py` from the terminal
2. Install the package with `pip` and use the provided `jb2atlas` command from the terminal (or inside a shell script that also runs `jupyter-book`, perhaps). 

We're still working out some logistical things on our end about getting the package on PyPi, so for now if you want to install the package locally we recommend using `poetry`. To do so, check out the `poetry` branch (`git checkout poetry`), install poetry (`pip install poetry`), and then run `poetry install --no-dev && poetry build` to install the dependences and build the wheel. Then, then run `pip install dist/jupyter_book_to_htmlbook-0.1.0-py3-none-any.whl`.


## Notes

* The `"pagenumrestart"` class is currently applied to the first chapter with parts (assuming that the chapters are numbered); this is a limitation to be overcome later (if there is a single-file chapter 1, a part, etc.)
* Currently, bibliography references are "opinionated," and are meant to follow CMS author-date in terms of in-text citations (no work has been done on the actual *references.html* yet).
