# Jupyter Book to HTMLBook

Takes a Jupyter Book and turns it into an HTMLBook-compliant project for consumption in Atlas, O'Reilly's book building tool. The script runs `jupyter-book` on your book directory (the one containing your *_config.yml* and *_toc.yml* files), and puts HTMLBook files in the specified target directory, updating atlas.json if it's provided.

**IMPORTANT**: We're now at >1.0.0, i.e., we have introduced a very breaking-change from the original version of the script! 

## Installation

**NOTE**: This tool requires Python ^3.9.

Install via the GitHub link:

```
pip install git+https://github.com/oreillymedia/jupyter-book-to-htmlbook.git
```

Or clone the repository, install poetry (`pip install poetry`), build the project (`poetry build`) and then install the locally-build wheel:

```
pip install dist/jupyter_book_to_htmlbook-X.X.X-py3-none-any.whl
```

## Usage

Usage:`jb2htmlbook [OPTIONS] SOURCE TARGET`

Help text: 

```
Usage: jb2htmlbook [OPTIONS] SOURCE TARGET

  Converts a Jupyter Book project into HTMLBook.

  Takes your SOURCE directory (which should contain your _toc and _config
  files), runs `jupyter-book`, converts and consolidates the output to
  HTMLBook, and places those files in the TARGET directory.

  If you for some reason don't want this script to run `jupyter-book` (`jb`),
  use the SKIP_JB_BUILD option.

  If you want to UPDATE_ATLAS_JSON, provide the relative path to the
  atlas.json file (will usually be just "atlas.json")

  Returns a json list of converted "files" as output for consumption by Atlas,
  O'Reilly's in-house publishing tool. Saves run information to
  jupyter_book_to_htmlbook_run.log

Arguments:
  SOURCE  [required]
  TARGET  [required]

Options:
  --atlas-json TEXT               Path to the book's atlas.json file
  --skip-jb-build                 Skip running `jupyter-book` as a part of
                                  this conversion
  --skip-numbering      Skip the numbering of In[]/Out[] code cells
  --include-root                  Include the 'root' file of the jupyter-book
                                  project
  --version
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.

```

## Current Known Limitations

* Jupyter Book can only process one metadata-named code-generated figure per file. The workaround for this is to save any resultant figures to disk and refer to them as any other figure.

## Release Notes

### 1.1.0

Features:
- Upgrade to Jupyter Book v.0.15.1

### 1.0.9

Bug fixes:
- Remove spans inside `<code>` tags that display incorrectly on the ORM learning platform.

### 1.0.8

Bug fixes:
- Part caption casing is preserved from `_toc.yaml`

### 1.0.7

Features:
- Add support for formal code examples in Python and R via the "example" cell tag
- Add support for glossaries
- Add basic support for bibtex bibliographies
- Align sidebar heading levels with changes in Atlas

Bug fixes:
- Fix bug with top-level heading IDs causing xrefs to fail
- Remove extraneous spacing in figure captions
- Remove epub-breaking attrs (incl. `valign` and `halign` on table cells)

### 1.0.6
- Add support for sidebars as described in the [Jupyter Book documentation](https://jupyterbook.org/en/stable/content/layout.html#sidebars-within-content)

### 1.0.1 - 1.0.5
- Add support for R via `rpy2` syntax in Notebooks
- Further quiet `jb build` to support Atlas builds
- Dependency security version updates
- Better code block handling, including `In[]/Out[]`
- Duplicate IDs are now removed programmatically globally in the book

### 1.0.0
- First release with CLI interface
- Supports automatically updating the atlas.json file with the list of converted jupyter book files

### 0.1.0 (untagged)
- First poetry version

### 0.0.0
- Initial conversion script targeted at a specific project.

