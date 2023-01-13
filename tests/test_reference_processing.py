import logging
import shutil
from bs4 import BeautifulSoup  # type: ignore
from jupyter_book_to_htmlbook.file_processing import process_chapter
from jupyter_book_to_htmlbook.reference_processing import (
        process_internal_refs,
        process_remaining_refs
    )


class TestInternalRefs:
    def test_process_internal_refs_reg_xrefs(self):
        """
        happy path internal ref processing for regular xrefs
        """
        chapter_text = """<a class="reference internal" href="example.html">
        cross reference text</a>"""
        chapter = BeautifulSoup(chapter_text, 'html.parser')
        result = process_internal_refs(chapter)
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
        result = process_internal_refs(chapter)
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
        result = process_internal_refs(chapter)
        assert result == chapter
        caplog.set_level(logging.DEBUG)
        assert "External image reference:" in caplog.text


class TestStandardRefs:
    """
    Tests around "std-ref" references, which appear as spans (in the case
    where Jupyter Book can't find the actual reference).
    """
    def test_process_xref_spans(self):
        """
        It appears that when an xref doesn't have a target jupyter knows about
        (e.g., in the case of examples), it puts them into spans. We should
        check for these and then convert them appropriately.
        """
        chapter = BeautifulSoup("""<p>And here follows a formal code example
(<span class="xref std std-ref">code_example</span>).
Note that the cell has an “example” tag added to its metadata.</p>""",
                                "html.parser")
        result = process_remaining_refs(chapter)
        xref = result.find("a", class_="xref")
        assert xref
        assert xref.get('data-type') == "xref"
        assert xref.get('href') == "#code_example"
        assert xref.string == "#code_example"

    def test_process_xref_spans_bad_ref(self, caplog):
        """
        In the unlikely case wherein we get a bad xref (i.e., one with
        spaces or code in it), we log that failure and do nothing
        """
        chapter = BeautifulSoup("""<p>And here follows a formal code example
(<span class="xref std std-ref">code example</span>). Another is
<span class="xref std std-ref"><span>some_</span><em>code_example</em></span>.
Note that the cell has an “example” tag added to its metadata.</p>""",
                                "html.parser")
        process_remaining_refs(chapter)
        caplog.set_level(logging.DEBUG)
        log = caplog.text
        assert "Failed to apply" in log
        assert "code example" in log
        assert "<em>code_example</em>" in log

    def test_examples_refs_in_chapter_processing(self, tmp_path):
        """
        More an integration test, ensuring that when we process a chapter
        the examples are data-typed as such, and that they still get their
        highlighting
        """
        test_env = tmp_path / 'tmp'
        test_out = test_env / 'output'
        test_env.mkdir()
        test_out.mkdir()
        shutil.copytree('tests/example_book/_build/html/notebooks',
                        test_env, dirs_exist_ok=True)

        process_chapter(test_env / "code_py.html",
                        test_env, test_out)
        with open(test_out / 'code_py.html') as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        xref = soup.find("a", class_="xref")
        assert xref
        assert xref.get("href") == "#hello_tim"
        assert xref.get("data-type") == "xref"
        assert xref.get("href") == "#hello_tim"
        assert xref.string == "#hello_tim"
