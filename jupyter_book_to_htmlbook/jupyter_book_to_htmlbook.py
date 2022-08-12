from .toc_processing import get_book_index
from .chapter_processing import process_chapter
from pathlib import Path
import shutil


def main(source_dir=Path('html/'), output_dir=Path('build/')):
    # setup
    image_dir = output_dir / 'images'
    image_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(f'{source_dir}/_images/', image_dir,
                    dirs_exist_ok=True)

    # get table of contents
    toc = get_book_index(source_dir)

    # process book files
    for element in toc:
        process_chapter(element, output_dir)


if __name__ == '__main__':
    main()
