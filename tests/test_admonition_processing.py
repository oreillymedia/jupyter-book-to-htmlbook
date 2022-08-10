import pytest
from bs4 import BeautifulSoup

from jupyter_book_to_htmlbook.admonition_processing import process_admonitions


@pytest.mark.parametrize(
        "admonitions", [
                "note",
                "warning",
                "tip",
                "caution",
                "important"
            ]
        )
def test_process_admonitions_no_title(admonitions):
    """
    Tests admonition processing for expected admonition types,
    assumes that the admonition title is just the admonition
    name (so we'll yank it per ORM style)
    """
    chapter_text = f"""
<div class="admonition {admonitions}">
<p class="admonition-title">{admonitions}</p>
<p>Lorem ipsum... </p>
</div>"""
    chapter = BeautifulSoup(chapter_text, 'html.parser')
    result = process_admonitions(chapter)
    assert str(result) == f"""
<div data-type="{admonitions}">

<p>Lorem ipsum... </p>
</div>"""


def test_process_admontitions_title():
    """
    Tests admonition processing in the case where there is an admonition
    title we want to keep
    """
    chapter_text = """
<div class="admonition note">
<p class="admonition-title">An Admonition Title</p>
<p>Lorem ipsum... </p>
</div>"""
    chapter = BeautifulSoup(chapter_text, 'html.parser')
    result = process_admonitions(chapter)
    assert str(result) == """
<div data-type="note">
<h1 class="admonition-title">An Admonition Title</h1>
<p>Lorem ipsum... </p>
</div>"""


def test_process_admonition_elements_in_title():
    """
    Tests admonition processing in the case where there is an admonition
    title that contains markup (against ORM style, but)
    """
    chapter_text = """
<div class="admonition note">
<p class="admonition-title">An <em>Admonition</em> Title</p>
<p>Lorem ipsum... </p>
</div>"""
    chapter = BeautifulSoup(chapter_text, 'html.parser')
    result = process_admonitions(chapter)
    assert str(result) == """
<div data-type="note">
<h1 class="admonition-title">An <em>Admonition</em> Title</h1>
<p>Lorem ipsum... </p>
</div>"""
