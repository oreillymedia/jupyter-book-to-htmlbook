import logging
from bs4 import BeautifulSoup  # type: ignore
from jupyter_book_to_htmlbook.reference_processing import process_interal_refs


class TestInternalRefs:
    def test_process_internal_refs_reg_xrefs(self):
        """
        happy path internal ref processing for regular xrefs
        """
        chapter_text = """<a class="reference internal" href="example.html">
        cross reference text</a>"""
        chapter = BeautifulSoup(chapter_text, 'html.parser')
        result = process_interal_refs(chapter)
        assert str(result) == '<a class="reference internal" data-type=' + \
                              '"xref" href="#example.html">#example.html</a>'

    def test_process_internal_refs_bibliograpy(self):
        """
        Should convert bib refs to spans containing CMS author-date style
        citations
        """
        text = """
<p>Finally, here is a citation <span id="id1">[<a class="reference internal"
href="#id6" title="Terry Baruch...">Baruch, 1993</a>]</span>.
And then some others <span id="id2">[<a class="reference internal"
href="#id5" title="Terry Aadams...">Aadams, 1993</a>]</span>,
<span id="id3">[<a class="reference internal" href="#id7"
title="Terry Carver...">Carver, 1993</a>]</span>.</p>
"""
        chapter = BeautifulSoup(text, 'html.parser')
        result = process_interal_refs(chapter)
        assert not result.find("a")
        assert "(Baruch 1993)" in result.find("span").contents

    def test_alert_on_external_images(self, caplog):
        """
        authors really shouldn't be linking out images, so we'll alert them
        when they do this, and not do any processing
        """
        chapter_text = """<a class="reference internal image-reference"
    href="http://example.com/example.png"><img alt="example"
    src="http://example.com/example.png" style="width:100px" /></a>"""
        chapter = BeautifulSoup(chapter_text, 'html.parser')
        result = process_interal_refs(chapter)
        assert result == chapter
        caplog.set_level(logging.DEBUG)
        assert "External image reference:" in caplog.text
