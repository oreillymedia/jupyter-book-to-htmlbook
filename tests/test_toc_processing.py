import pytest
from pathlib import Path
from jupyter_book_to_htmlbook.toc_processing import get_book_toc


class TestGetBookToc:
    """
    Tests for pulling the books table of contents from the
    _toc.yaml file in the jupyter book source directory.

    The files listed in _toc.yml will appear with the same relative
    file structure inside the _build/html directory, so we'll prepend
    that to the expected paths always.
    """

    def test_simple_toc(self, tmp_path):
        """
        happy-path, can we pull the list as expected
        """
        with open(tmp_path / '_toc.yml', 'wt') as f:
            f.write("""# Table of contents
# Learn more at https://jupyterbook.org/customize/toc.html

format: jb-book
root: intro
chapters:
- file: notebooks/preface
- file: notebooks/ch01
- file: notebooks/ch02""")
        result = get_book_toc(tmp_path)
        assert result == [tmp_path / "_build/html/notebooks/preface.html",
                          tmp_path / "_build/html/notebooks/ch01.html",
                          tmp_path / "_build/html/notebooks/ch02.html"]

    def test_toc_with_sections(self, tmp_path):
        """
        happy-path, can we pull the list as expected
        """
        with open(tmp_path / '_toc.yml', 'wt') as f:
            f.write("""# Table of contents
# Learn more at https://jupyterbook.org/customize/toc.html

format: jb-book
root: intro
chapters:
- file: notebooks/preface
- file: notebooks/ch01.00
  sections:
    - file: notebooks/ch01.01
    - file: notebooks/ch01.02
- file: ch02
""")
        result = get_book_toc(tmp_path)
        assert result == [tmp_path / "_build/html/notebooks/preface.html",
                          [tmp_path / "_build/html/notebooks/ch01.00.html",
                           tmp_path / "_build/html/notebooks/ch01.01.html",
                           tmp_path / "_build/html/notebooks/ch01.02.html"],
                          tmp_path / "_build/html/ch02.html"]

    # edge cases
    def test_no_book_toc(self, caplog):
        """ Edge case: what if there's no _toc file? Don't continue. """
        with pytest.raises(SystemExit):
            get_book_toc(Path())
        assert "Can't find" in caplog.text

    def test_non_jb_book_format(self, tmp_path, caplog):
        """ We should only support the "jb-book" format """

        with open(tmp_path / '_toc.yml', 'wt') as f:
            f.write("format: jb-article")

        with pytest.raises(SystemExit):
            get_book_toc(tmp_path)

        assert "jb-book" in caplog.text

    def test_bad_yaml(self, tmp_path, caplog):
        """
        YAML should be formatted as expected, or at least there
        ought to be a format defined
        """
        with open(tmp_path / '_toc.yml', 'wt') as f:
            f.write("not-format: article")

        with pytest.raises(SystemExit):
            get_book_toc(tmp_path)

        assert "malformed" in caplog.text.lower()
