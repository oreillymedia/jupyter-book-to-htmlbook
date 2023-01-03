import shutil
from bs4 import BeautifulSoup  # type: ignore
from jupyter_book_to_htmlbook.reference_processing import (
        add_glossary_datatypes
    )
from jupyter_book_to_htmlbook.file_processing import (
        apply_datatype,
        process_chapter
    )


class TestGlossary:
    """
    Tests for glossaries, both the expected Jupyter Book kind as well as
    inferred glossaries via bare definition lists in a "glossary.ipynb" file.
    """

    def test_simple_glossary_conversion(self):
        """
        Test data-typing of Jupyter Book-style glossaries
        """
        chapter = BeautifulSoup(
            """<dl class="glossary simple">
            <dt id="term-Gloss-Term">
            Gloss <em>Term</em> with <code>code</code><a class="headerlink"
            href="#term-Gloss-Term" title="Permalink to this term">#</a></dt>
            <dd><p>Gloss definition.</p></dd>
            <dt id="term-Gloss-Term-2">
            Gloss Term 2<a class="headerlink" href="#term-Gloss-Term-2"
            title="Permalink to this term">#</a></dt><dd><p>Gloss definition 2.
            </p></dd>""", "html.parser")
        result = add_glossary_datatypes(chapter)
        assert result.find("dl")["data-type"] == "glossary"
        assert result.find("dt")["data-type"] == "glossterm"
        assert result.find("dfn")  # docbook compatibility, presumably
        assert result.find("dd")["data-type"] == "glossdef"
        assert not result.find("a", class_="headerlink")
        # ensures that any extra tags are preserved in the <dfn> tag
        assert len(result.find("dfn").contents) == 4

    def test_chapter_for_glossary_data_type(self, tmp_path):
        """
        Given a "glossary.*" filename, we want the main/chapter section to have
        a "glossary" data-type
        """
        test_env = tmp_path / 'tmp'
        test_env.mkdir()
        shutil.copytree('tests/example_book/_build/html/notebooks',
                        test_env, dirs_exist_ok=True)
        with open(test_env / 'glossary.html') as f:
            text = f.read()
        chapter = BeautifulSoup(text, "lxml").find_all('section')[0]
        apply_datatype(chapter, "glossary")
        assert chapter["data-type"] == "glossary"

    def test_file_processsing_for_glossary(self, tmp_path):
        """
        Given a "glossary.*" filename, we want the main/chapter section to have
        a "glossary" data-type
        """
        test_env = tmp_path / 'tmp'
        test_out = test_env / 'output'
        test_env.mkdir()
        test_out.mkdir()
        shutil.copytree('tests/example_book/_build/html/notebooks',
                        test_env, dirs_exist_ok=True)

        process_chapter(test_env / "glossary.html", test_env, test_out)
        with open(test_out / 'glossary.html') as f:
            text = f.read()
            assert '<section data-type="glossary"' in text
            # ensure we get the jupyter book-style glossaries
            assert '<dl class="glossary simple" data-type="glossary"' in text
            # ensure we also tag the regular definition list-based glossaries
            assert '<dl class="simple myst" data-type="glossary"' in text
