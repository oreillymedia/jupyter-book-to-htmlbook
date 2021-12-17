from toc_processing import *
from chapter_processing import *
import os

# default html directory
html_dir = 'html/'

def main():
    os.system(f'cp {html_dir}/_images/* images/')
    toc = get_book_index(html_dir)
    for element in toc:
        # print(element)
        process_chapter(element)

    # move the images


if __name__ == '__main__':
    main()