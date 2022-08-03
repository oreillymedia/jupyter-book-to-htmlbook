from toc_processing import get_book_index
from chapter_processing import process_chapter
import os
from pathlib import Path

# default source html directory
html_dir = Path('html/')

# default build directory
build_dir = Path('build/')
image_dir = build_dir / 'images'


def main():
    image_dir.mkdir(parents=True, exist_ok=True)
    os.system(f'cp {html_dir}/_images/* {image_dir}')
    toc = get_book_index(html_dir)
    for element in toc:
        process_chapter(element, build_dir)


if __name__ == '__main__':
    main()
