import logging
import pytest
import re
from bs4 import BeautifulSoup  # type: ignore
from jupyter_book_to_htmlbook.code_processing import (
        process_code,
        number_codeblock,
    )
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

    def test_numbering_in_process_code(self, code_example_python):
        """
        Ensure that when we process a chapter, code blocks are
        numbered correctly
        """
        result = process_code(code_example_python)
        assert "In [1]: " in str(result)
        assert "Out[1]: " in str(result)
        assert "In [2]: " in str(result)
        assert "Out[2]: " in str(result)

    def test_warning_if_non_in_or_out_highlight(self, caplog):
        """
        Possible edge case is if a highlighted div doesn't have a
        grandparent `cell_input` or `cell_output` class. We want to
        log this if it happens.
        """
        type_error = BeautifulSoup("""<div class="no"><div class="no">
                            <div class="highlight type_err">failures!</div>
                            </div></div>
                            """, 'html.parser')
        key_error = BeautifulSoup(
                            '<div class="highlight key_err">failures!</div>',
                            'html.parser')
        caplog.set_level(logging.DEBUG)
        process_code(type_error)
        process_code(key_error)
        log = caplog.text
        assert "Unable to apply cell numbering" in log
        assert "key_err" in log
        assert "type_err" in log

    def test_dont_number_out_blocks_if_in_block_is_hidden(self):
        """
        If an author is purposely hiding the input cell, we shouldn't
        go on to number the output cell.
        """
        example_content = BeautifulSoup("""
                        <div class="cell tag_hide-input docutils container">
                        <div class="cell_output docutils container">
                        <div class="output stream">
                        <div class="highlight"><pre><span></span>(323, 4)
                        </pre></div>
                        </div></div>""", "html.parser")
        result = process_code(example_content)
        assert "Out[0]" not in str(result)


class TestNumbering:
    """
    Tests around the numbering and indentation of code cells
    """

    def test_in_blocks_are_numbered(self, code_example_python):
        """
        Input blocks should be marked as such and numbered via the usual
        Jupyter Notebook formatting of `In [##]`.

        Numbering inputs should add the `In` marker, return the element,
        and return the next marker
        """
        in_div = code_example_python.find('div', class_="cell_input")
        in_pre = in_div.find('pre')
        result = number_codeblock(in_pre, 1)
        assert "In [1]: " in str(result)

    @pytest.mark.parametrize("numbering", [1, 20, 100])
    def test_in_blocks_are_indented_correctly(self,
                                              code_example_python,
                                              numbering):
        """
        Input blocks should be marked as such and numbered via the usual
        Jupyter Notebook formatting of `In [##]`, and subsequent lines of
        code should be indented likewise.

        This will test
        """
        # gather info about preprocess indentation, "live" for durability
        in_div = code_example_python.find('div', class_='cell_input')
        in_pre = in_div.find('pre')
        preprocess_indentations = re.findall(r'(\n\s*)', str(in_pre))
        expected_indentations = [ind + (" " * len(f"In [{numbering}]: "))
                                 for ind in preprocess_indentations]
        # add numbering
        result = number_codeblock(in_pre, numbering)

        # check indents
        postprocess_indentations = re.findall(r'(\n\s*)',
                                              str(result))
        assert postprocess_indentations == expected_indentations

    def test_out_blocks_are_numbered(self, code_example_python):
        """
        Output blocks should be marked as such and numbered via the usual
        Jupyter Notebook formatting of `Out[##]`.
        """
        in_div = code_example_python.find('div', class_="cell_input")
        in_pre = in_div.find('pre')
        result = number_codeblock(in_pre, 1, in_block=False)
        assert "Out[1]: " in str(result)

    @pytest.mark.parametrize("numbering", [1, 20, 100])
    def test_out_blocks_are_indented_correctly(self,
                                               code_example_python,
                                               numbering):
        """
        Output blocks should be marked as such and numbered via the usual
        Jupyter Notebook formatting of `Out[##]`, and subsequent lines of
        code should be indented likewise.
        """
        # gather info about preprocess indentation, "live" for durability
        in_div = code_example_python.find_all('div', class_='cell_output')[1]
        in_pre = in_div.find('pre')
        preprocess_indentations = re.findall(r'(\n\s*)', str(in_pre))
        expected_indentations = [ind + (" " * len(f"Out[{numbering}]: "))
                                 for ind in preprocess_indentations]
        # add numbering
        result = number_codeblock(in_pre, numbering, False)

        # check indents
        postprocess_indentations = re.findall(r'(\n\s*)',
                                              str(result))
        assert postprocess_indentations == expected_indentations
