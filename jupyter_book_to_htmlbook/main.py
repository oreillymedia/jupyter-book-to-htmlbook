import logging
import shutil
import typer
from pathlib import Path
from importlib import metadata
from typing import Optional
from .toc_processing import get_book_index
from .chapter_processing import process_chapter


app = typer.Typer()

__version__ = metadata.version(__package__)


def show_version(value: bool):
    if value:
        print(f"{__version__}")
        raise typer.Exit()


@app.command()  # note that docstring serves as --help text
def jupter_book_to_htmlbook(
        source: str,
        target: str,
        skip_jb_build: Optional[bool] = False,
        version: Optional[bool] = typer.Option(None, "--version",
                                               callback=show_version,
                                               is_eager=True)
        ):
    """
    Converts a Jupyter Book project into HTMLBook.

    Takes your SOURCE directory (which should contain your _toc and _config
    files), runs `jupyter-book`, converts and consolidates the output to
    HTMLBook, and places those files in the TARGET directory.

    If you for some reason don't want this script to run `jupyter-book` (`jb`),
    use the SKIP_JB_BUILD option.

    Returns a json list of converted "files" as output for consumption by
    Atlas, O'Reilly's in-house publishing tool. Saves run information to
    jupyter_book_to_htmlbook_run.log
    """
    # use paths
    source_dir = Path(source) / '_build/html'
    output_dir = Path(source) / target

    # create output_dir (and wiping it is OK)
    output_dir.mkdir(exist_ok=True)

    # setup logging
    log_fn = str(output_dir / 'jb2htmlbook.log')
    logging.basicConfig(filename=log_fn,
                        encoding='utf-8',
                        format='%(levelname)s: %(message)s',
                        level=logging.DEBUG)
    logging.info(f'App version: {__version__}')
    logging.info(f'Source: {source}, Target: {target}')

    # run `jupyter-book` (or log that we didn't)
    if not skip_jb_build:
        # NOTE: that we have to run it as a subprocess because it doesn't
        # seem like they've designed it to be importable.
        # Bonus is that it keeps the command similar to what an author will be
        # using locally.
        import subprocess
        jb_info = subprocess.run(['jupyter-book', 'build',
                                 source])
        logging.info("jupyter-book run stdout: " + str(jb_info.stdout))
        logging.info("jupyter-book run stderr: " + str(jb_info.stderr))
    else:
        logging.info("Skipping jupyter-book run...")

    # setup images directory
    if Path(f'{source_dir}/_images').exists():
        image_dir = output_dir / 'images'
        image_dir.mkdir(parents=True, exist_ok=True)
        shutil.copytree(f'{source_dir}/_images/', image_dir,
                        dirs_exist_ok=True)
    else:
        logging.info("No images in the source book")

    # get table of contents
    toc = get_book_index(source_dir)

    # create a list to return as output
    processed_files = []

    # process book files
    for element in toc:
        file = process_chapter(element, output_dir)
        # add the extra quotes because we want them in the returned string
        processed_files.append(f'"{target}/{file}"')

    print(",".join(processed_files))


def main():
    app()
