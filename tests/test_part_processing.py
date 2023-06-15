from pathlib import Path
from jupyter_book_to_htmlbook.file_processing import process_part


class TestPartProcessing:
    """
    Tests around turning part placeholder Paths into real part files
    """

    def test_process_part(self, tmp_path):
        """
        Take a path with the appropriate part designation, and create
        a file with the appropriate numbering and name
        """
        part_path = Path(tmp_path / '_jb_part-1-Name-of-Part.html')
        result = process_part(part_path, tmp_path)
        assert result == 'part-1.html'
        with open(tmp_path / 'part-1.html') as f:
            assert f.read() == """
<div xmlns="http://www.w3.org/1999/xhtml" data-type="part" id="part-1">
<h1>Name of Part</h1>
</div>""".lstrip()

    def test_process_part_bad_name(self, tmp_path, caplog):
        part_path = Path(tmp_path / '_jb_part-1.html')
        result = process_part(part_path, tmp_path)
        assert result is None
        assert "unable to parse part information" in caplog.text.lower()

    def test_process_part_id_is_correct(self, tmp_path):
        """
        Sanity check test to confirm that a prior bug isn't (re)introduced
        """
        part_path = Path(tmp_path / '_jb_part-20-Part.html')
        result = process_part(part_path, tmp_path)
        assert result == 'part-20.html'
        with open(tmp_path / 'part-20.html') as f:
            text = f.read()
            assert text.find('id="part-20"') > 0
