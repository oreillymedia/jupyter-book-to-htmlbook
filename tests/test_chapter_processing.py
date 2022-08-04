import shutil
from bs4 import BeautifulSoup
from jupyter_book_to_htmlbook.chapter_processing import (
        clean_chapter,
        compile_chapter_parts,
        move_span_ids_to_sections
)
from jupyter_book_to_htmlbook.toc_processing import get_book_index


def test_chapter_cleans():
    """ test that we're ripping out the things we want to """
    chapter_text = r"""<style>body: 13px</style>
<script src="js/js.js" />
<table border="7">
<tr><td>Hello</td><td>World</td></tr>
</table>
<p style="text-decoration: underline">Lorem ipsum</p>
<h2><span class="section-number">19.1.1.
</span>Issues with Linear Regression<a class="headerlink"
href="#issues-with-linear-regression" title="Permalink to this headline">¶</a>
/h2>
<div class="cell tag_hide-input docutils container">
div class="cell_input docutils container">
<pre> some thing </pre>
</div>
</div>"""
    chapter = BeautifulSoup(chapter_text, 'html.parser')
    result = clean_chapter(chapter)
    assert str(result) == """

<table>
<tr><td>Hello</td><td>World</td></tr>
</table>
<p>Lorem ipsum</p>
<h2>Issues with Linear Regression
/h2&gt;
<div class="cell tag_hide-input docutils container">
div class="cell_input docutils container"&gt;
<pre> some thing </pre>
</div>
</h2>"""


def test_move_span_ids_to_sections():
    """
    Atlas requires that cross reference targets sections so that
    the text will appear as expected. This test is to confirm that
    the ids we added ("sec-") to the invisible spans earlier for cross
    referencing are then applied to the parent section.
    """
    chapter_text = """
<section class="section" data-type="sect2" id="types-of-bias">
<span id="sec-biastypes"></span><h2>Types of Bias</h2>
<p>Bias comes in many forms!</p>"""
    chapter = BeautifulSoup(chapter_text, 'html.parser')
    result = move_span_ids_to_sections(chapter)
    assert str(result) == """
<section class="section" data-type="sect2" id="sec-biastypes">
<h2>Types of Bias</h2>
<p>Bias comes in many forms!</p></section>"""


def test_compile_chapter_parts_happy_path_non_numbered(tmp_path):
    """
    happy path for taking an ordered list of chapter paths
    and then returning a <section> delimited chapter

    This one goes with a nonnumbered toc
    """
    test_env = tmp_path / 'tmp'
    test_env.mkdir()
    shutil.copytree('tests/example_html', test_env, dirs_exist_ok=True)
    toc = get_book_index(test_env)
    # first item is the intro file, so let's check on the first "chapter"
    result = compile_chapter_parts(toc[1])
    # the resulting section should have a data-type of "chapter"
    assert result["data-type"] == "chapter"  # type: ignore
    # number of level-1 subsections should be one less than the group
    number_of_sections = len(
            result.find_all(attrs={"data-type": "sect1"}))  # type: ignore
    number_of_sections_expected = len(toc[1]) - 1  # type: ignore
    assert number_of_sections == number_of_sections_expected


def test_compile_chapter_parts_happy_path_numbered(tmp_path):
    """
    happy path for taking an ordered list of chapter paths
    and then returning a <section> delimited chapter

    This one goes with a nonnumbered toc
    """
    test_env = tmp_path / 'tmp'
    test_env.mkdir()
    shutil.copytree('tests/example_html_numbered',
                    test_env, dirs_exist_ok=True)
    toc = get_book_index(test_env)
    # first item is the intro file, so let's check on the first "chapter"
    result = compile_chapter_parts(toc[1])
    # the resulting section should have a data-type of "chapter"
    assert result["data-type"] == "chapter"  # type: ignore
    # number of level-1 subsections should be one less than the group
    number_of_sections = len(
            result.find_all(attrs={"data-type": "sect1"}))  # type: ignore
    number_of_sections_expected = len(toc[1]) - 1  # type: ignore
    assert number_of_sections == number_of_sections_expected

