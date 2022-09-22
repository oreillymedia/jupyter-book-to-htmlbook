import logging
import sys
from pathlib import Path
from yaml import load  # type: ignore
try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader


def get_book_toc(src_dir: Path) -> list:
    """
    Takes the 'genindex' file from a Jupyter Book HTML site and returns a
    list of chapter URIs and lists of chapter URIs where there is more than one
    file per chapter.
    """
    compiled_toc = []

    def _path(file_stub, src_dir=src_dir):
        return Path(src_dir / f'_build/html/{file_stub}.html')

    try:
        with open(src_dir / "_toc.yml") as f:
            toc = load(f.read(), SafeLoader)
            # exit if we see some format other than jb-book
            try:
                if toc["format"] != "jb-book":
                    logging.error("Unsupported jupyter book format: " +
                                  toc["format"] + ". The only supported" +
                                  " format is 'jb-book'.")
                    sys.exit()
            except KeyError:
                logging.error("Malformed _toc.yml file. Please see " +
                              "jupyterbook.org for correct syntax.")
                sys.exit()

            # add "root"
            compiled_toc.append(_path(toc["root"]))

            # process chapters
            for chapter in toc['chapters']:
                try:  # if chapter has sections
                    chapter_files: list[Path] = []
                    # append first file
                    chapter_files.append(_path(chapter['file']))

                    for section in chapter["sections"]:
                        chapter_files.append(_path(section['file']))

                    compiled_toc.append(chapter_files)

                except KeyError:  # chapter _doesn't_ have sections
                    compiled_toc.append(_path(chapter['file']))

    except FileNotFoundError:
        logging.error("Can't find the _toc.yml file. Ensure you're " +
                      "specifying a valid jupyter book project as the SOURCE.")
        sys.exit()

    return compiled_toc
