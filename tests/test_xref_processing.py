import logging
from bs4 import BeautifulSoup  # type: ignore
from jupyter_book_to_htmlbook.xref_processing import process_interal_refs


def test_process_internal_refs_reg_xrefs():
    """
    happy path internal ref processing for regular xrefs
    """
    chapter_text = """<a class="reference internal" href="example.html">
    cross reference text</a>"""
    chapter = BeautifulSoup(chapter_text, 'html.parser')
    result = process_interal_refs(chapter)
    assert str(result) == '<a class="reference internal" data-type="xref" ' + \
                          'href="#example.html">#example.html</a>'


def test_process_internal_refs_bibliograpy():
    """
    Should convert bib refs to spans containing CMS author-date style citations
    """
    # note the variable format change was just to make the lines break better
    ctxt = '<p>For a more detailed breakdown, see ' + \
           '<span id="1">[<a class="reference internal" href="../../' + \
           'references.html#id35">Leek and Peng, 2015</a>]</span>.</p>' + \
           '<p>In the next section, we’ll talk about...</p>'
    chapter = BeautifulSoup(ctxt, 'html.parser')
    result = process_interal_refs(chapter)
    assert str(result) == "<p>For a more detailed breakdown, see <span>" + \
                          "(Leek and Peng 2015)</span>.</p><p>In the next " + \
                          "section, we’ll talk about...</p>"


def test_alert_on_external_images(caplog):
    """
    authors really shouldn't be linking out images, so we'll alert them when
    they do this, and not do any processing
    """
    chapter_text = """<a class="reference internal image-reference"
href="http://example.com/example.png"><img alt="example"
src="http://example.com/example.png" style="width:100px" /></a>"""
    chapter = BeautifulSoup(chapter_text, 'html.parser')
    result = process_interal_refs(chapter)
    assert result == chapter
    caplog.set_level(logging.DEBUG)
    assert "External image reference:" in caplog.text
