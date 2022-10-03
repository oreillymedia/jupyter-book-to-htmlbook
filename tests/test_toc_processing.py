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
        assert result == [tmp_path / '_build/html/intro.html',
                          tmp_path / "_build/html/notebooks/preface.html",
                          tmp_path / "_build/html/notebooks/ch01.html",
                          tmp_path / "_build/html/notebooks/ch02.html"]

    def test_toc_with_file_extensions(self, tmp_path):
        """
        Apparently one _can_ include a file extension in the toc. This
        shouldn't cause our script to fail, but rather we ought just remove
        them
        """
        with open(tmp_path / '_toc.yml', 'wt') as f:
            f.write("""# Table of contents
# Learn more at https://jupyterbook.org/customize/toc.html

format: jb-book
root: intro.ipynb
chapters:
- file: notebooks/preface.md
- file: notebooks/ch01.ipynb
- file: notebooks/ch02.rst""")
        result = get_book_toc(tmp_path)
        assert result == [tmp_path / '_build/html/intro.html',
                          tmp_path / "_build/html/notebooks/preface.html",
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
        assert result == [tmp_path / '_build/html/intro.html',
                          tmp_path / "_build/html/notebooks/preface.html",
                          [tmp_path / "_build/html/notebooks/ch01.00.html",
                           tmp_path / "_build/html/notebooks/ch01.01.html",
                           tmp_path / "_build/html/notebooks/ch01.02.html"],
                          tmp_path / "_build/html/ch02.html"]

    def test_toc_with_parts(self, tmp_path):
        """
        Support part syntax.

        Parts are merely given captions, but we'll create "dummy" paths
        from which we will extract the part title and create the file
        downstream in chapter processing.
        """
        with open(tmp_path / '_toc.yml', 'wt') as f:
            f.write("""format: jb-book
root: intro
parts:
  - caption: Name of Part 1
    chapters:
    - file: part1/chapter1
    - file: part1/chapter2
      sections:
      - file: part1/section2-1
  - caption: Name of Part 2
    chapters:
    - file: part2/chapter1
    - file: part2/chapter2
      sections:
      - file: part2/section2-1""")
        result = get_book_toc(tmp_path)
        assert result == [
                tmp_path / '_build/html/intro.html',
                tmp_path / '_build/html/_jb_part-1-name-of-part-1.html',
                tmp_path / '_build/html/part1/chapter1.html',
                [tmp_path / '_build/html/part1/chapter2.html',
                 tmp_path / '_build/html/part1/section2-1.html'],
                tmp_path / '_build/html/_jb_part-2-name-of-part-2.html',
                tmp_path / '_build/html/part2/chapter1.html',
                [tmp_path / '_build/html/part2/chapter2.html',
                 tmp_path / '_build/html/part2/section2-1.html']
               ]

    def test_toc_with_parts_move_preface(self, tmp_path):
        """
        Jupyter Book part syntax doesn't seem to support the notion of a
        'preface', so we should intelligently move any *preface* files
        ahead of the first part so atlas doesn't get confused.

        Should accommodate having extra stuff around the filename
        """
        with open(tmp_path / '_toc.yml', 'wt') as f:
            f.write("""format: jb-book
root: intro
parts:
  - caption: Name of Part 1
    chapters:
    - file: /path-to/00-Preface.ipynb
    - file: part1/chapter2
      sections:
      - file: part1/section2-1
  - caption: Name of Part 2
    chapters:
    - file: part2/chapter1
    - file: part2/chapter2
      sections:
      - file: part2/section2-1""")
        result = get_book_toc(tmp_path)
        assert result == [
                tmp_path / '_build/html/intro.html',
                tmp_path / '_build/html/path-to/00-Preface.html',
                tmp_path / '_build/html/_jb_part-1-name-of-part-1.html',
                [tmp_path / '_build/html/part1/chapter2.html',
                 tmp_path / '_build/html/part1/section2-1.html'],
                tmp_path / '_build/html/_jb_part-2-name-of-part-2.html',
                tmp_path / '_build/html/part2/chapter1.html',
                [tmp_path / '_build/html/part2/chapter2.html',
                 tmp_path / '_build/html/part2/section2-1.html']
               ]

    def test_toc_with_parts_move_preface_but_multiple(self, tmp_path):
        """
        If multiple "prefaces" are found, make sure they are correctly ordered
        at the beginning of the toc
        """
        with open(tmp_path / '_toc.yml', 'wt') as f:
            f.write("""format: jb-book
root: intro
parts:
  - caption: Name of Part 1
    chapters:
    - file: /path-to/preface
    - file: /path-to/second-preface
    - file: part1/chapter2
      sections:
      - file: part1/chapter-section
  - caption: Name of Part 2
    chapters:
    - file: part2/chapter1
    - file: part2/chapter2
      sections:
      - file: part2/section2-1""")
        result = get_book_toc(tmp_path)
        assert result == [
                tmp_path / '_build/html/intro.html',
                tmp_path / '_build/html/path-to/preface.html',
                tmp_path / '_build/html/path-to/second-preface.html',
                tmp_path / '_build/html/_jb_part-1-name-of-part-1.html',
                [tmp_path / '_build/html/part1/chapter2.html',
                 tmp_path / '_build/html/part1/chapter-section.html'],
                tmp_path / '_build/html/_jb_part-2-name-of-part-2.html',
                tmp_path / '_build/html/part2/chapter1.html',
                [tmp_path / '_build/html/part2/chapter2.html',
                 tmp_path / '_build/html/part2/section2-1.html']
               ]

    def test_prefaces_in_sections_do_not_move(self, tmp_path):
        """ if a "*preface*" is in a section:, however, do not move it """
        with open(tmp_path / '_toc.yml', 'wt') as f:
            f.write("""format: jb-book
root: intro
parts:
  - caption: Name of Part 1
    chapters:
    - file: /path-to/preface
    - file: /path-to/second-preface
    - file: part1/chapter2
      sections:
      - file: part1/chapter-section
      - file: part1/preface-1
  - caption: Name of Part 2
    chapters:
    - file: example""")
        result = get_book_toc(tmp_path)
        assert result == [
                tmp_path / '_build/html/intro.html',
                tmp_path / '_build/html/path-to/preface.html',
                tmp_path / '_build/html/path-to/second-preface.html',
                tmp_path / '_build/html/_jb_part-1-name-of-part-1.html',
                [tmp_path / '_build/html/part1/chapter2.html',
                 tmp_path / '_build/html/part1/chapter-section.html',
                 tmp_path / '_build/html/part1/preface-1.html'],
                tmp_path / '_build/html/_jb_part-2-name-of-part-2.html',
                tmp_path / '_build/html/example.html'
               ]

    def test_toc_with_parts_no_captions(self, tmp_path, caplog, capsys):
        """
        Error out if parts don't have captions, and inform the user why
        """
        with open(tmp_path / '_toc.yml', 'wt') as f:
            f.write("""format: jb-book
root: intro
parts:
    chapters:
    - file: part1/chapter1
    - file: part1/chapter2
      sections:
      - file: part1/section2-1
    chapters:
    - file: part2/chapter1
    - file: part2/chapter2
      sections:
      - file: part2/section2-1""")
        with pytest.raises(SystemExit):
            get_book_toc(tmp_path)
        assert "missing part caption" in caplog.text.lower()
        assert "missing part caption" in \
            capsys.readouterr().out.lower()

    # edge cases
    def test_no_book_toc(self, caplog, capsys):
        """ Edge case: what if there's no _toc file? Don't continue. """
        with pytest.raises(SystemExit):
            get_book_toc(Path())
        assert "Can't find" in caplog.text
        assert "Can't find" in capsys.readouterr().out

    def test_non_jb_book_format(self, tmp_path, caplog, capsys):
        """ We should only support the "jb-book" format """

        with open(tmp_path / '_toc.yml', 'wt') as f:
            f.write("format: jb-article")

        with pytest.raises(SystemExit):
            get_book_toc(tmp_path)

        assert "jb-book" in caplog.text
        assert "jb-book" in capsys.readouterr().out.lower()

    def test_bad_yaml(self, tmp_path, caplog, capsys):
        """
        YAML should be formatted as expected, or at least there
        ought to be a format defined
        """
        with open(tmp_path / '_toc.yml', 'wt') as f:
            f.write("not-format: article")

        with pytest.raises(SystemExit):
            get_book_toc(tmp_path)

        assert "malformed" in caplog.text.lower()
        assert "malformed" in capsys.readouterr().out.lower()
