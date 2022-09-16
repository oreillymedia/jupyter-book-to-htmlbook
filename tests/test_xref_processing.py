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


def test_process_internal_refs_image_refs():
    """
    Sometimes images are wrapped in a tags, when really they should be
    informal figures; this test makes sure of that
    """
    chapter_text = """<div>
<a class="reference internal image-reference" href="../../_images/example.jpg">
<img alt="../../_images/example.jpg" src="../../_images/example.jpg"
style="width: 375.0px; height: 500.0px;" /></a>
</div>"""
    chapter = BeautifulSoup(chapter_text, 'html.parser')
    result = process_interal_refs(chapter)
    assert str(result) == """<div>
<figure class="informal">
<img alt="../../_images/example.jpg" src="images/example.jpg"/></figure>
</div>"""


def test_process_internal_refs_image_refs_skip_existing_figs():
    """
    We don't want to double wrap images if they're already in figures
    """
    chapter_text = """<div class="figure align-default" id="example">
<a class="reference internal image-reference" href="../../_images/example.jpg">
<img alt="../../_images/example.jpg" src="../../_images/example.jpg"
style="width: 375.0px; height: 500.0px;" /></a>
<p class="caption"><span class="caption-number">
Fig. 8.1 </span><span class="caption-text">An example image.
Here is another sentence.</span>
<a class="headerlink" href="#scorecard" title="Permalink to this image">¶</a>
</p>
</div>"""
    chapter = BeautifulSoup(chapter_text, 'html.parser')
    result = process_interal_refs(chapter)
    assert result == chapter


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
