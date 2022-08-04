import shutil
import os
import pytest
from pathlib import Path
from bs4 import BeautifulSoup
from jupyter_book_to_htmlbook.chapter_processing import (
        clean_chapter,
        compile_chapter_parts,
        move_span_ids_to_sections,
        process_chapter
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


def test_compile_chapter_parts_keyerror(capsys):
    """
    It's too much of a pain to mock the circumstances in which this
    might happen, so we'll force it and prove it works.
    """
    ordered_list = [Path('tests/example_html/error_forcers/keyerror.html')]
    compile_chapter_parts(ordered_list)
    output = capsys.readouterr().out.rstrip()
    assert output.rstrip() == """Error: 'id' in keyerror.html
It's possible there is no empty span here and likely is not a problem."""


def test_compile_chapter_parts_typeerror(capsys):
    """
    It's too much of a pain to mock the circumstances in which this
    might happen, so we'll force it and prove it works.
    """
    ordered_list = [Path('tests/example_html/error_forcers/typeerror.html')]
    compile_chapter_parts(ordered_list)
    output = capsys.readouterr().out.rstrip()
    assert output.rstrip() == """Error: 'NoneType' object is not subscriptable in typeerror.html
It's possible there is no empty span here and likely is not a problem."""


def test_process_chapter_single_chapter_file(tmp_path):
    """
    happy path for chapter processing a single chapter file
    """
    test_env = tmp_path / 'tmp'
    test_out = test_env / 'output'
    test_env.mkdir()
    test_out.mkdir()
    shutil.copytree('tests/example_html', test_env, dirs_exist_ok=True)
    toc = get_book_index(test_env)
    # first item is the intro file, so let's check on the first "chapter"
    process_chapter(toc[0], test_out)
    # the resulting section should have a data-type of "chapter"
    assert os.path.exists(test_out / 'intro.html')


def test_process_chapter_chapter_with_subfiles(tmp_path):
    """
    happy path for chapter processing a chapter with subfiles
    """
    test_env = tmp_path / 'tmp'
    test_out = test_env / 'output'
    test_env.mkdir()
    test_out.mkdir()
    shutil.copytree('tests/example_html', test_env, dirs_exist_ok=True)
    toc = get_book_index(test_env)
    # first item is the intro file, so let's check on the first "chapter"
    process_chapter(toc[1], test_out)
    # the resulting section should have a data-type of "chapter"
    assert os.path.exists(test_out / 'ch01.html')


def test_process_chapter_no_section(tmp_path):
    """
    confirm that the xml namespace gets added even if there aren't any
    <div class="section"> tags
    """
    test_env = tmp_path / 'tmp'
    test_out = test_env / 'output'
    test_env.mkdir()
    test_out.mkdir()
    shutil.copytree('tests/example_html', test_env, dirs_exist_ok=True)
    # first item is the intro file, so let's check on the first "chapter"
    process_chapter(test_env / 'error_forcers/nosection.html', test_out)
    # the resulting section should have a data-type of "chapter"
    with open(test_out / 'nosection.html') as f:
        text = f.read()
        assert text.find('xmlns="http://www.w3.org/1999/xhtml"') > -1


def test_process_chapter_totally_invalid_file(tmp_path, capsys):
    """
    if we ever try to process something that's super malformed, don't,
    and alert the user
    """
    test_env = tmp_path / 'tmp'
    test_out = test_env / 'output'
    test_env.mkdir()
    test_out.mkdir()
    shutil.copytree('tests/example_html', test_env, dirs_exist_ok=True)
    # first item is the intro file, so let's check on the first "chapter"
    process_chapter(test_env / 'error_forcers/malformed.html', test_out)
    # the resulting section should have a data-type of "chapter"
    output = capsys.readouterr().out.rstrip()
    assert "is malformed" in output


@pytest.mark.parametrize(
        "datatype", [
            "preface",
            "colophon"
            ]
        )
def test_process_chapter_guessing_datatypes(tmp_path, datatype):
    """
    happy path for guessing datatypes, i.e, they're allowed
    """
    test_env = tmp_path / 'tmp'
    test_out = test_env / 'output'
    test_env.mkdir()
    test_out.mkdir()
    test_file_path = test_env / f'{datatype}.html'
    shutil.copytree('tests/example_html', test_env, dirs_exist_ok=True)
    shutil.move(test_env / 'intro.html', test_file_path)
    process_chapter(test_file_path, test_out)
    # the resulting section should have a data-type of "datatype"
    with open(test_out / f'{datatype}.html') as f:
        text = f.read()
        assert text.find(f'data-type="{datatype}') > -1


@pytest.mark.parametrize(
        "datatype", [
            ("prereqs", "preface"),
            ("author_bio", "afterword")
            ]
        )
def test_process_chapter_guessing_datatypes_non_allowed(tmp_path, datatype):
    """
    confirm that the default front/backmatter data types are applied
    in the case that we get a guessed-at front/backmatter chapter title
    """
    test_env = tmp_path / 'tmp'
    test_out = test_env / 'output'
    test_env.mkdir()
    test_out.mkdir()
    test_file_path = test_env / f'{datatype[0]}.html'
    shutil.copytree('tests/example_html', test_env, dirs_exist_ok=True)
    shutil.move(test_env / 'intro.html', test_file_path)
    process_chapter(test_file_path, test_out)
    # the resulting section should have a data-type of "datatype"
    with open(test_out / f'{datatype[0]}.html') as f:
        text = f.read()
        assert text.find(f'data-type="{datatype[1]}') > -1


def test_chapter_process_confirm_remove_span(tmp_path):
    """
    happy path for chapter processing with numbered sections
    """
    test_env = tmp_path / 'tmp'
    test_out = test_env / 'output'
    test_env.mkdir()
    test_out.mkdir()
    shutil.copytree('tests/example_html_numbered',
                    test_env, dirs_exist_ok=True)
    toc = get_book_index(test_env)
    # first item is the intro file, so let's check on the first "chapter"
    process_chapter(toc[1], test_out)
    # the resulting section should have a data-type of "chapter"
    assert os.path.exists(test_out / 'ch01.html')

