import pytest
import re
from bs4 import BeautifulSoup  # type: ignore
from jupyter_book_to_htmlbook.code_processing import process_code
from pathlib import Path


@pytest.fixture
def code_example_python():
    chapter = Path(
                     "tests/example_book/_build/html/notebooks/code.html"
                  ).read_text()
    return BeautifulSoup(chapter, 'lxml')


class TestCodeProcessing:
    """
    Tests around handing of code blocks in Jupyter Books
    """

    def test_add_python_datatype(self, code_example_python):
        """
        Jupyter Book is putting highlight information in surrounding divs;
        we should add the HTMLBook data-type="programlisting" and
        data-code-language if we see that it's a highlight-ipython3 class

        NOTE: while Jupyter can support other languages, we're currently
        targeting ONLY python, since that's what seems to be primarily built
        into Jupyter Book.
        """
        result = process_code(code_example_python)
        assert result.find('pre')['data-type'] == "programlisting"
        assert result.find('pre')['data-code-language'] == "python"

    def test_extraneous_span_classes_are_removed(self, code_example_python):
        """
        We want to remove the highlighting classes that Jupyter Book is adding
        so that our processor doesn't have conflicts/get confused.

        NOTE: The classless spans don't seem to affect the Atlas highlighter,
        so best to leave them in to avoid accidentally removing information.
        """
        result = process_code(code_example_python)
        assert not re.search(r'<span class="[a-z]{1,2}"', str(result))
