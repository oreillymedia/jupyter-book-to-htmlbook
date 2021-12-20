from toc_processing import *
from chapter_processing import *
import os
from pathlib import Path

# default html directory
html_dir = 'html/'

# default build directory
build_dir = Path('build/')
image_dir = build_dir / 'images'

def main():
    image_dir.mkdir(parents=True, exist_ok=True)
    os.system(f'cp {html_dir}/_images/* {image_dir}') # note: no windows support
    toc = get_book_index(html_dir)
    for element in toc:
        process_chapter(element, build_dir)


if __name__ == '__main__':
    main()