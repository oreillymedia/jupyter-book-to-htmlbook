import logging
import sys
from pathlib import Path
from yaml import load  # type: ignore
try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader


def _path(file_stub, src_dir):
    return Path(src_dir / f'_build/html/{file_stub}.html')


def _log_print_and_exit(message):
    """
    helper function to log a script-ending error message, print it,
    and exit with an error code indicating failure
    """
    logging.error(message)
    print(message)
    sys.exit(1)


def get_book_toc(src_dir: Path) -> list:
    """
    Takes the 'genindex' file from a Jupyter Book HTML site and returns a
    list of chapter URIs and lists of chapter URIs where there is more than one
    file per chapter.
    """
    compiled_toc = []

    try:
        with open(src_dir / "_toc.yml") as f:
            toc = load(f.read(), SafeLoader)
            # exit if we see some format other than jb-book
            try:
                if toc["format"] != "jb-book":
                    message = ("Unsupported jupyter book format: " +
                               toc["format"] + ". The only supported" +
                               " format is 'jb-book'.")
                    _log_print_and_exit(message)
            except KeyError:
                message = ("Malformed _toc.yml file. Please see " +
                           "jupyterbook.org for correct syntax.")
                _log_print_and_exit(message)

            # add "root"
            compiled_toc.append(_path(toc["root"], src_dir))

            if "parts" in toc.keys():
                compiled_toc.extend(process_parts(toc["parts"], src_dir))
            else:
                compiled_toc.extend(process_chapters(toc["chapters"], src_dir))

    except FileNotFoundError:
        message = "Can't find the _toc.yml file. Ensure you're " + \
                  "specifying a valid jupyter book project as the SOURCE."
        _log_print_and_exit(message)

    return compiled_toc


def process_chapters(chapter_list, src_dir) -> list:
    """
    takes a `chapters:` list, optionally with sections
    and returns a list (or list of) of Paths
    """
    chapters = []
    for chapter in chapter_list:
        try:  # if chapter has sections
            chapter_files: list[Path] = []
            # append first file
            chapter_files.append(_path(chapter['file'], src_dir))

            for section in chapter["sections"]:
                chapter_files.append(_path(section['file'], src_dir))

            chapters.append(chapter_files)

        except KeyError:  # chapter _doesn't_ have sections
            chapters.append(_path(chapter['file'], src_dir))

    return chapters


def process_parts(parts, src_dir):
    """ part processing function"""
    part_number = 0
    part_files = []
    for part in parts:
        part_number += 1  # increment numbering
        # create a distinct placeholder Path for downstream processing
        try:
            part_title = part["caption"].replace(' ', '-').lower()
        except TypeError:  # because it's looking for a string, getting an int
            message = ("Missing part caption in _toc.yml. " +
                       "Part captions are required.")
            _log_print_and_exit(message)
        part_stub = f'_jb_part-{part_number}-{part_title}'
        part_files.append(_path(part_stub, src_dir))
        # now add the chapters
        part_files.extend(
            process_chapters(part["chapters"], src_dir)
        )
    return part_files
