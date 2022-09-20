import logging
import os
import pytest
import shutil
from bs4 import BeautifulSoup  # type: ignore
from jupyter_book_to_htmlbook.chapter_processing import (
        clean_chapter,
        compile_chapter_parts,
        move_span_ids_to_sections,
        process_chapter
)


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


def test_compile_chapter_parts_happy_path(tmp_path):
    """
    happy path for taking an ordered list of chapter paths
    and then returning a <section> delimited chapter
    """
    test_env = tmp_path / 'tmp'
    test_env.mkdir()
    shutil.copytree('tests/example_book/_build/html/notebooks',
                    test_env, dirs_exist_ok=True)

    result = compile_chapter_parts([
        test_env / 'ch02.00.html',
        test_env / 'ch02.01.html',
        test_env / 'ch02.02.html',
        ])
    # the resulting section should have a data-type of "chapter"
    assert result["data-type"] == "chapter"
    # number of level-1 subsections should be one less than the group
    number_of_sections = len(
            result.find_all(attrs={"data-type": "sect1"}))
    number_of_sections_expected = 2  # the first html file doesn't get one
    assert number_of_sections == number_of_sections_expected


def test_compile_chapter_parts_keyerror(tmp_path, caplog):
    """
    It's too much of a pain to mock the circumstances in which this
    might happen, so we'll force it and prove it works.
    """
    caplog.set_level(logging.DEBUG)
    with open(tmp_path / 'keyerror.html', 'wt') as f:
        f.write("""
<section class="tex2jax_ignore mathjax_ignore section" id="example">
<h1><span class="section-number">19.
/span>Example<a class="headerlink" href="#example"
title="Permalink to this headline">¶</a></h1>
<p>This chapter is under development. When it’s finished, this note will be
removed.</p>
</section>""")
    ordered_list = [tmp_path / 'keyerror.html']
    compile_chapter_parts(ordered_list)
    assert """'id' in keyerror.html""" in caplog.text


def test_compile_chapter_parts_typeerror(tmp_path, caplog):
    """
    It's too much of a pain to mock the circumstances in which this
    might happen, so we'll force it and prove it works.
    """
    caplog.set_level(logging.DEBUG)
    with open(tmp_path / 'typeerror.html', 'wt') as f:
        f.write("""
<section class="tex2jax_ignore mathjax_ignore" id="example">
<h1>Example<a class="headerlink" href="#example"
title="Permalink to this headline">¶</a></h1>
</section>""")
    ordered_list = [tmp_path / 'typeerror.html']
    compile_chapter_parts(ordered_list)
    assert (
            "'NoneType' object is not subscriptable in typeerror.html"
            ) in caplog.text


def test_process_chapter_single_chapter_file(tmp_path, capsys):
    """
    happy path for chapter processing a single chapter file

    also ensures that our function is returning what we expect it to
    """
    test_env = tmp_path / 'tmp'
    test_out = test_env / 'output'
    test_env.mkdir()
    test_out.mkdir()
    shutil.copy('tests/example_book/_build/html/notebooks/ch01.html',
                test_env / 'ch01.html')
    result = process_chapter((test_env / 'ch01.html'), test_out)
    # first item is the intro file, so let's check on the first "chapter"
    assert os.path.exists(test_out / 'ch01.html')
    # check on return
    assert "ch01.html" in result


def test_process_chapter_with_subfiles(tmp_path):
    """
    happy path for chapter processing a chapter with subfiles
    """
    test_env = tmp_path / 'tmp'
    test_out = test_env / 'output'
    test_env.mkdir()
    test_out.mkdir()
    shutil.copytree('tests/example_book/_build/html/notebooks',
                    test_env, dirs_exist_ok=True)

    result = process_chapter([
        test_env / 'ch02.00.html',
        test_env / 'ch02.01.html',
        test_env / 'ch02.02.html',
        ], test_out)
    # first item is the intro file, so let's check on the first "chapter"
    # the resulting section should have a data-type of "chapter"
    assert "ch02" in result
    assert os.path.exists(test_out / 'ch02.00.html')


def test_process_chapter_no_section(tmp_path):
    """
    confirm that the xml namespace gets added even if there aren't any
    <div class="section"> tags
    """
    test_out = tmp_path / 'out'
    test_out.mkdir()
    with open(tmp_path / 'nosection.html', 'wt') as f:
        f.write("""<main>
<section>
    <h1>Hello!</h1>
</section>
</main>""")
    process_chapter(tmp_path / 'nosection.html', test_out)
    # the resulting section should have a data-type of "chapter"
    with open(test_out / 'nosection.html') as f:
        text = f.read()
        assert text.find('xmlns="http://www.w3.org/1999/xhtml"') > -1


def test_process_chapter_totally_invalid_file(tmp_path, caplog):
    """
    if we ever try to process something that's super malformed, don't,
    and alert the user
    """
    with open(tmp_path / 'malformed.html', 'wt') as f:
        f.write("""<div>
    <h1>Hello!</h1>
</div>""")
    # first item is the intro file, so let's check on the first "chapter"
    result = process_chapter(tmp_path / 'malformed.html')
    # the resulting section should have a data-type of "chapter"
    caplog.set_level(logging.DEBUG)
    assert "is malformed" in caplog.text
    assert result is None


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
    shutil.copy('tests/example_book/_build/html/intro.html', test_file_path)
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
def test_process_chapter_guessing_datatypes_inferred(tmp_path, datatype):
    """
    confirm that the default front/backmatter data types are applied
    in the case that we get an inferred front/backmatter chapter title
    """
    test_env = tmp_path / 'tmp'
    test_out = test_env / 'build'
    test_env.mkdir()
    test_out.mkdir()
    test_file_path = test_env / f'{datatype[0]}.html'
    shutil.copy('tests/example_book/_build/html/intro.html', test_file_path)
    process_chapter(test_file_path, test_out)
    # the resulting section should have a data-type of "datatype"
    with open(test_out / f'{datatype[0]}.html') as f:
        text = f.read()
        assert text.find(f'data-type="{datatype[1]}') > -1
