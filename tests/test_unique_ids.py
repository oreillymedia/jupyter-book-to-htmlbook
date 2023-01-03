import re
from bs4 import BeautifulSoup  # type: ignore
from typer.testing import CliRunner
from jupyter_book_to_htmlbook.reference_processing import process_ids

runner = CliRunner()


def test_unique_ids():
    """
    IDs should be unique; duplicated IDs should be numbered sequentially
    and those changes should be logged. Given a list, duplicate ids should
    be updated (with randomized number) and then returned to the list
    """
    existing_ids = ["foo"]
    chapter = BeautifulSoup("""<h1 id="foo">Hello</h1>""", "html.parser")
    result, chapter_ids = process_ids(chapter, existing_ids)
    assert re.search(r'id="foo_[0-9]+', str(result))
    assert re.match(r'foo_[0-9]+', chapter_ids[0])


def test_xrefs_are_updated_when_ids_change():
    """
    If an id is changed, we should search for any internal references to it
    and update that cross ref with the new ID.

    The assumption is that any reference to a duplicate ID supposes that the
    ID in the same file is meant.
    """
    existing_ids = ["foo"]
    chapter = BeautifulSoup("""<h1 id="foo">Hello</h1>
            <p><a href="#foo">link to heading</a></p>
            <p><a href="#foo">another link to heading</a></p>
            """, "html.parser")
    result, chapter_ids = process_ids(chapter, existing_ids)
    assert re.search(r'#foo_[0-9]+', str(result))
