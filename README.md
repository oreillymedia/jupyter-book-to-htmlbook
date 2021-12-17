# Jupyter Book to HTMLBook

Takes a Jupyter Book (in HTML) and turns it into an HTMLBook-compliant project.

Supposes that you're in a book repo and that the output of the jupyter book script 
is in a _./html_ directory. You can change this default in 
*jupyter_book_to_htmlbook/jupyter_book_to_htmlbook.py*.

## Notes

* The `"pagenumrestart"` class is currently applied to the first chapter with parts (assuming that the chapters are numbered); this is a limitation to be overcome later (if there is a single-file chapter 1, a part, etc.)
* Currently, bibliography references are "opinionated," and are meant to follow CMS 
author-date in terms of in-text citations (no work has been done on the actual 
*references.html* yet).