from toc_processing import *
from chapter_processing import *
import os

# default html directory
html_dir = 'html/'

def main():
    os.system(f'cp {html_dir}/_images/* images/') # note: no windows support
    toc = get_book_index(html_dir)
    for element in toc:
        process_chapter(element)


if __name__ == '__main__':
    main()