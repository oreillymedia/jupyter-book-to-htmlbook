import logging
import pytest
import re
import shutil
from bs4 import BeautifulSoup  # type: ignore
from jupyter_book_to_htmlbook.code_processing import (
        process_code,
        process_inline_code,
        number_codeblock,
        process_code_examples
    )
from jupyter_book_to_htmlbook.file_processing import process_chapter
from pathlib import Path


@pytest.fixture
def code_example_python():
    chapter = Path(
                     "tests/example_book/_build/html/notebooks/code_py.html"
                  ).read_text()
    return BeautifulSoup(chapter, 'lxml')


@pytest.fixture
def code_example_r():
    return BeautifulSoup("""
<div class="cell docutils container">
<div class="cell_input docutils container">
<div class="highlight-ipython3 notranslate"><div class="highlight">
<pre><span></span><span class="o">%%</span><span class="k">R</span>
## R
5^8
</pre></div></div></div><div class="cell_output docutils container">
<div class="output stream highlight-myst-ansi notranslate">
<div class="highlight"><pre><span></span>[1] 390625
</pre></div></div></div></div>""", "html.parser")


@pytest.fixture
def code_example_data_type():
    return BeautifulSoup("""<div class="cell tag_example docutils container">
<div class="cell_input docutils container">
<div class="highlight-ipython3 notranslate"><div class="highlight">
<pre><span></span><span class="c1"># hello</span>
<span class="c1"># An example example title</span>

<span class="k">def</span> <span class="nf">h</span><span class="p">():</span>
    <span class="k">pass</span>
</pre></div>
</div>
</div>
</div>
""", "html.parser")


@pytest.fixture
def code_example_data_type_r():
    return BeautifulSoup("""
<div class="cell tag_example docutils container">
<div class="cell_input docutils container">
<div class="highlight-ipython3 notranslate"><div class="highlight">
<pre><span></span><span class="o">%%</span><span class="k">R</span>
# example_r
# A formal R example
## R
5^8
</pre></div></div></div>
<div class="cell_output docutils container">
<div class="output stream highlight-myst-ansi notranslate">
<div class="highlight">
<pre><span></span>[1] 390625
</pre></div></div></div></div>
""", "html.parser")


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

    def test_add_r_datatype(self, code_example_r):
        """
        Jupyter Book should add the data-code-language appropriately IF
        we are seeing that we're loading `%load_ext rpy2.ipython` and we
        have a block with `%%R` at the beginning. If it's a "python" notebook
        the highlight-ipython3 class is being applied, but that's not really
        relevant so it should be removed.
        """
        result = process_code(code_example_r)
        check_div = result.find_all('pre')[0]
        assert check_div.get('data-code-language') == "r"
        assert "highlight-ipython3" not in str(check_div.parent['class'])

    def test_add_r_datatype_removes_rpy2_flag(self, code_example_r):
        """
        In order to tell the notebook that a cell is an R cell (in an otherwise
        Python notebook), authors must include `%%R` at the beginning of the
        cell. Per author feedback, we should remove that, since if there are
        two languages in the text, the preferred distinguishing mechanism is
        comments (e.g., `##R`).
        """
        result = process_code(code_example_r)
        # check second div, since first div is the `load_ext` command
        check_div = result.find_all('pre')[0]
        # note that these are two separate spans, and we're using "find" since
        # we only want to confirm that they're not at the beginning
        assert not check_div.find('span', string="%%")
        assert not check_div.find_all('span', string="R")

    def test_add_r_datatype_removes_newline(self, code_example_r):
        """
        In addition to removing the `%%R` characters, we should start the
        block at the first non-whitespace character as you'd expect, so in
        our test case, we're looking to ensure that the second member of
        check_div.contents *doesn't* start with a newline.
        """
        result = process_code(code_example_r)
        check_div = result.find_all('pre')[1]
        assert check_div.contents[1].find('\n') != 0

    def test_add_r_formatting_edge_case(self):
        """
        While not common anymore in Python >= 3.6, there is still the
        possibility that older string interpolation syntax might include
        `%%R` somewhere in the code, so we want to ensure that we're only
        tagging blocks that _start_ with `%%R` as `r` language blocks.
        """
        snippet = """
<div class="cell docutils container">
<div class="cell_input docutils container">
<div class="highlight-ipython3 notranslate"><div class="highlight"><pre>
<span></span><span class="n">r</span> <span class="o">=</span>
<span class="s1">&#39;s = </span><span class="si">%r</span>
<span class="se">\n</span><span class="s1">print(s</span>
<span class="si">%%</span><span class="s1">R)&#39;</span>
<span class="nb">print</span><span class="p">(</span>
<span class="n">r</span><span class="o">%</span><span class="k">r</span>
)
</pre></div>
</div>
</div>
"""
        soup = BeautifulSoup(snippet, 'html.parser')
        result = process_code(soup)
        assert 'data-code-language="r"' not in str(result)

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
        number_codeblock(in_pre, 0)
        assert "In [1]: " in str(in_pre)

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
        number_codeblock(in_pre, numbering)

        # check indents
        postprocess_indentations = re.findall(r'(\n\s*)', str(in_pre))
        assert postprocess_indentations == expected_indentations

    def test_out_blocks_are_numbered(self, code_example_python):
        """
        Output blocks should be marked as such and numbered via the usual
        Jupyter Notebook formatting of `Out[##]`.
        """
        in_div = code_example_python.find('div', class_="cell_output")
        in_pre = in_div.find('pre')
        number_codeblock(in_pre, 1)
        assert "Out[1]: " in str(in_pre)

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
        number_codeblock(in_pre, numbering)

        # check indents
        postprocess_indentations = re.findall(r'(\n\s*)', str(in_pre))
        assert postprocess_indentations == expected_indentations

    def test_r_blocks_are_indented_corrently(self, code_example_r):
        """
        Ensure R blocks are indented correctly as well. Note that we're testing
        without `%%R` since that'll be removed prior to numbering, and,
        frustratingly, the results are different.
        """
        in_div = BeautifulSoup("""<div class="cell_input docutils container">
<div><div class="highlight">
<pre data-code-language="r" data-type="programlisting">## R
5^8
</pre></div>
</div>
</div>""", 'html.parser')
        in_pre = in_div.find('pre')
        preprocess_indentations = re.findall(r'(\n\s*)', str(in_pre))
        expected_indentations = [ind + (" " * len("In [1]: "))
                                 for ind in preprocess_indentations]
        # need to process, numbering with that
        number_codeblock(in_pre, 0)

        # check indents
        postprocess_indentations = re.findall(r'(\n\s*)', str(in_pre))
        assert postprocess_indentations == expected_indentations


class TestCodeExamples:
    """
    Tests around code blocks that should be rendered as "Examples" in the text,
    signaled by the "tag_example" class appended to the cell div
    """

    def test_example_datatype_is_added(self, code_example_data_type):
        """
        Test that when we see "tag_example" in a class list, the
        appropriate "example" data type is added
        """
        result = process_code_examples(code_example_data_type)
        example_div = result.find("div", class_="tag_example")
        assert example_div.get("data-type") == "example"

    def test_example_uuid_is_added(self, code_example_data_type):
        """
        Test that when we see "tag_example" in a class list, the
        appropriate id for the example (based on first comment in
        code) is applied to the div with the "example" data-type
        """
        result = process_code_examples(code_example_data_type)
        example_div = result.find("div", class_="tag_example")
        assert example_div["id"] == "hello"

    def test_example_heading_is_added(self, code_example_data_type):
        """
        Test that when we see "tag_example" in a class list, the
        appropriate heading for the example (based on 2nd comment in
        code) is added in an h5 tag to the div with the "example" data-type
        """
        result = process_code_examples(code_example_data_type)
        example_div = result.find("div", class_="tag_example")
        assert example_div.find("h5")
        assert example_div.find("h5").string == "An example example title"

    def test_example_signal_comments_are_removed(self, code_example_data_type):
        """
        We don't need (or want) the signaling names/headings to appear in
        the final book, so let's ensure those are removed, but also that
        we're not leaving a bunch of extra space there.
        """
        result = process_code_examples(code_example_data_type)
        example_pre = result.find("pre")
        assert not example_pre.find("span", class_="c1", string="# hello")
        assert not example_pre.find("span", class_="c1",
                                    string="# An example example title")
        assert "\n" not in example_pre.contents[0:3]
        assert "\n\n" not in example_pre.contents[0:3]

    def test_malformed_example_missing_uuid(self, caplog):
        """
        Ensure that we're logging failures (e.g., when an author doesn't
        include both a uuid and title)
        """
        expect_fail = BeautifulSoup("""
<div class="cell tag_example docutils container">
<div class="cell_input docutils container">
<div class="highlight-ipython3 notranslate"><div class="highlight">
<pre><span></span><span class="c1"># This is an example title</span>

<span class="k">def</span> <span class="nf">h</span><span class="p">():</span>
    <span class="k">pass</span></pre></div></div></div></div>
""", "html.parser")
        caplog.set_level(logging.DEBUG)
        result = process_code_examples(expect_fail)
        log = caplog.text
        assert "Unable to apply example formatting" in log
        assert not result.find("div", class_="highlight").get("data-type")

    def test_malformed_example_missing_title(self, caplog):
        """
        Ensure that we're logging failures (e.g., when an author doesn't
        include both a uuid and title)
        """
        expect_fail = BeautifulSoup("""
<div class="cell tag_example docutils container">
<div class="cell_input docutils container">
<div class="highlight-ipython3 notranslate"><div class="highlight">
<pre><span></span><span class="c1"># hello</span>

<span class="k">def</span> <span class="nf">h</span><span class="p">():</span>
    <span class="k">pass</span></pre></div></div></div></div>
""", "html.parser")
        caplog.set_level(logging.DEBUG)
        result = process_code_examples(expect_fail)
        log = caplog.text
        assert "Unable to apply example formatting" in log
        assert not result.find("div", class_="highlight").get("data-type")

    def test_malformed_example_does_not_destroy_chapter(self, caplog):
        """
        Once we had a bad return given failures; this test is to
        ensure that even if we don't add example formatting, we also
        do not only return the bad block.
        """
        expect_fail = BeautifulSoup("""
<div id="do_not_lose_me">Hello!</div>
<div class="cell tag_example docutils container">
<div class="cell_input docutils container">
<div class="highlight-ipython3 notranslate"><div class="highlight">
<pre><span></span><span class="c1"># This is an example title</span>

<span class="k">def</span> <span class="nf">h</span><span class="p">():</span>
    <span class="k">pass</span></pre></div></div></div></div>
""", "html.parser")
        caplog.set_level(logging.DEBUG)
        result = process_code_examples(expect_fail)
        log = caplog.text
        assert "Unable to apply example formatting" in log
        assert not result.find("div", class_="highlight").get("data-type")
        assert result.find("div", id="do_not_lose_me")

    def test_malformed_example_with_extra_comments_later(self, caplog):
        """
        Ensure that we're logging failures (e.g., when an author doesn't
        include both a uuid and title)
        """
        expect_fail = BeautifulSoup("""
<div class="cell tag_example docutils container">
<div class="cell_input docutils container">
<div class="highlight-ipython3 notranslate"><div class="highlight">
<pre><span></span><span class="c1"># hello</span>

<span class="k">def</span> <span class="nf">h</span><span class="p">():</span>
    <span class="k">pass</span><span class="c1">FAIL!</span></pre></div></div>
</div></div>""", "html.parser")
        caplog.set_level(logging.DEBUG)
        result = process_code_examples(expect_fail)
        log = caplog.text
        assert "Missing first two line comments for" in log
        assert not result.find("div", class_="highlight").get("data-type")

    def test_examples_and_highlight_in_chapter_processing(self, tmp_path):
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

        examples = soup.find_all("div", class_="tag_example")
        assert len(examples) == 2
        for example_div in examples:
            assert example_div["data-type"] == "example"
            assert example_div.find("h5")
            assert example_div.find("pre")["data-code-language"] == "python"

    def test_example_pulls_in_output(self):
        """
        If the code example has any output, it should be included in the
        example div
        """
        chapter = BeautifulSoup("""
<div class="cell tag_example docutils container">
<div class="cell_input docutils container">
<div class="highlight-ipython3 notranslate"><div class="highlight">
<pre><span></span><span class="c1"># hello_tim_with_output</span>
<span class="c1"># An example, but with output</span>

<span class="n">hello</span><span class="p">()</span>
</pre></div>
</div>
</div>
<div class="cell_output docutils container">
<div class="output stream highlight-myst-ansi notranslate">
<div class="highlight"><pre><span></span>Hello, Tim! Nice to meet you!
</pre></div>
</div>
</div>
</div>""", "html.parser")
        result = process_code_examples(chapter)
        example_div = result.find("div", class_="tag_example")
        assert example_div.find("div", class_="cell_output")

    def test_example_in_r(self, code_example_data_type_r):
        result = process_code_examples(code_example_data_type_r)
        example_div = result.find("div", class_="tag_example")
        assert example_div.get("data-type") == "example"
        assert example_div.get("id") == "example_r"
        assert example_div.find("h5", string="A formal R example")
        assert ("# example_r\n# A formal R example\n" not in
                example_div.find("pre").contents[3])

    def test_examples_and_highlight_in_chapter_processing_r(self, tmp_path):
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

        process_chapter(test_env / "code_r.html",
                        test_env, test_out)
        with open(test_out / 'code_r.html') as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        examples = soup.find_all("div", class_="tag_example")
        assert len(examples) == 1
        assert examples[0]["data-type"] == "example"
        assert examples[0].find("h5")
        assert examples[0].find("pre")["data-code-language"] == "r"

    def test_examples_malformed_r(self, caplog):
        """
        What do we do if an example R block doesn't have the correct
        comment hashes? We do nothing!
        """
        malformed_example = BeautifulSoup("""
<div class="cell tag_example docutils container">
<div class="cell_input docutils container">
<div class="highlight-ipython3 notranslate"><div class="highlight">
<pre><span></span><span class="o">%%</span><span class="k">R</span>
# example_r
## R
5^8
</pre></div></div></div>
</div>""", "html.parser")
        result = process_code_examples(malformed_example)
        example_div = result.find("div", class_="tag_example")
        caplog.set_level(logging.DEBUG)
        log = caplog.text
        assert not example_div.get("data-type") == "example"
        assert not example_div.get("id") == "example_r"
        assert not example_div.find("h5", string="A formal R example")
        assert result == malformed_example
        assert "Missing first two line comments for" in log


class TestInlineCode:
    """
    Smoke tests around the translation of inline code
    """

    def test_unwrap_inline_spans(self):
        """
        We should not allow spans inside inline code
        """

        html = BeautifulSoup("""<p>Some text with
<code><span class="pre">code</span></code>.</p>""",
                             "html.parser")
        result = process_inline_code(html)

        assert not result.find("span")
        assert str(result.find("code")) == "<code>code</code>"

    def test_unwrap_inline_spans_does_not_affect_pre(self,
                                                     code_example_data_type):
        expected = str(code_example_data_type)
        result = process_inline_code(code_example_data_type)
        assert str(result) == expected

