import shutil
from bs4 import BeautifulSoup  # type: ignore
from jupyter_book_to_htmlbook.file_processing import (
        apply_datatype,
        process_chapter
    )
from jupyter_book_to_htmlbook.reference_processing import process_citations


class TestBibliography:
    """
    Tests targeting "bibliography" content included in the book, including:
    * End of book "bibliography" appendix
    * End-of-file / chapter bibliographies

    NOTE: Tests against citations/references should be found in the
    test_references.py file.
    """

    def test_bib_appx_datatype(self, tmp_path):
        """
        Given a "bibliography.*" filename, we want the main/chapter section to
        have an "appendix" data-type
        """
        test_env = tmp_path / 'tmp'
        test_env.mkdir()
        shutil.copytree('tests/example_book/_build/html/',
                        test_env, dirs_exist_ok=True)
        with open(test_env / 'bibliography.html') as f:
            text = f.read()
        chapter = BeautifulSoup(text, "lxml").find_all('section')[0]
        apply_datatype(chapter, "bibliography")
        assert chapter["data-type"] == "appendix"

    def test_bib_appx_to_author_date(self):
        """
        Given the standard output (based on the resultant bibliography.html
        file) from Jupyter Book, bibliographical citations should be in an
        unordered list with an "author-date" style applied to the list.
        """
        chapter = BeautifulSoup("""
<dl class="citation">
<dt class="label" id="id2"><span class="brackets">Aad93</span></dt>
<dd><p>Terry Aadams. The title of the work. <em>The name of the journal</em>,
4(2):201–213, 7 1993. An optional note.</p>
</dd>
<dt class="label" id="id3"><span class="brackets">Bar93</span></dt>
<dd><p>Terry Baruch. <em>The title of the work</em>. Volume 4 of 10. The name
of the publisher, The address, 3 edition, 7 1993. ISBN 3257227892. An optional
note.</p>
</dd>
<dt class="label" id="id4"><span class="brackets">Car93</span></dt>
<dd><p>Terry Carver. The title of the work. How it was published, The address
of the publisher, 7 1993, An optional note.</p>
</dd>
</dl>
""", "html.parser")
        result = process_citations(chapter)
        assert not result.find("dl")
        assert "author-date" in result.find("ul")["class"]
        assert len(result.find_all("li")) == 3

    def test_bib_gets_moved_to_end(self, tmp_path):
        """
        An in-chapter bibliography should be moved to the end of the main
        chapter section.
        """
        test_env = tmp_path / 'tmp'
        test_out = test_env / 'output'
        test_env.mkdir()
        test_out.mkdir()
        shutil.copytree('tests/example_book/_build/html/notebooks/',
                        test_env, dirs_exist_ok=True)
        result = process_chapter([
            test_env / 'ch02.00.html',
            test_env / 'ch02.01.html',
            test_env / 'ch02.02.html',
            ], test_env, test_out)[0]
        with open(test_out / result, "rt") as f:
            soup = BeautifulSoup(f.read(), "lxml")

        assert soup.find_all("section")[-1]["id"] == "bibliography"
        assert soup.find_all("section")[-1].find("ul", class_="author-date")

    def test_sub_bibs_get_combined_appropriately(self, tmp_path):
        """
        If multiple sub-chapters have bibliographies, they should be
        combined into a single (unsorted) list

        NOTE: This is not the ideal solution, but a "works enough for now"
        compromise.
        """
        test_env = tmp_path / 'tmp'
        test_out = test_env / 'output'
        test_env.mkdir()
        test_out.mkdir()
        shutil.copytree('tests/example_book/_build/html/notebooks/',
                        test_env, dirs_exist_ok=True)
        result = process_chapter([
            test_env / 'ch02.00.html',
            test_env / 'ch02.01.html',
            test_env / 'ch02.01.html',
            test_env / 'ch02.02.html',
            ], test_env, test_out)[0]
        with open(test_out / result, "rt") as f:
            soup = BeautifulSoup(f.read(), "lxml")
        assert len(soup.find_all("section", id="bibliography")) == 1
        assert len(soup.find("section", id="bibliography").find_all("li")) == 6
