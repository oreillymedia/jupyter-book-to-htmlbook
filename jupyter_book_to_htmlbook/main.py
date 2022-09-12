import typer
import shutil
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
        version: Optional[bool] = typer.Option(None, "--version",
                                               callback=show_version,
                                               is_eager=True)
        ):
    """
    Converts a Jupyter Book project into HTMLBook.

    Takes your SOURCE directory (which should contain your _toc and _config
    files), runs `jupyter-book`, converts and consolidates the output to
    HTMLBook, and places those files in the TARGET directory.

    Returns a json list of converted "files" as output for consumption by
    Atlas, O'Reilly's in-house publishing tool.
    """
    source_dir = Path(source)
    output_dir = Path(target)

    image_dir = output_dir / 'images'
    image_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(f'{source_dir}/_images/', image_dir,
                    dirs_exist_ok=True)

    # get table of contents
    toc = get_book_index(source_dir)

    # process book files
    for element in toc:
        process_chapter(element, output_dir)


def main():
    app()
