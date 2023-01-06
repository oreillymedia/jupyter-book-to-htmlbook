from bs4 import BeautifulSoup  # type: ignore
from jupyter_book_to_htmlbook.helpers import base_soup


def test_get_base_soup_happy_path():
    """
    Ensure that we can get our base/root soup from
    an element
    """
    soup = BeautifulSoup("""
<div id="root"><div><div>
<p><a id="test">a</a></p>
</div></div></div>""", "html.parser")
    element = soup.find("a", id="test")
    base = base_soup(element)
    assert base == soup


def test_get_base_soup_no_parents():
    """
    Ensure that we can get our base/root soup from
    an element, and if it's itself, we return itself
    """
    soup = BeautifulSoup("""
<div id="root"><div><div>
<p><a id="test">a</a></p>
</div></div></div>""", "html.parser")
    element = soup.find("div", id="root")
    base = base_soup(element)
    assert base == soup
