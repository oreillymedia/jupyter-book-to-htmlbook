import logging
import os
import pytest
import shutil
from bs4 import BeautifulSoup  # type: ignore
from jupyter_book_to_htmlbook.file_processing import (
        clean_chapter,
        compile_chapter_parts,
        move_span_ids_to_sections,
        process_chapter,
        process_chapter_single_file
)


class TestChapterProcess:
    """ chapter tests """

    def test_chapter_cleans(self):
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

    def test_move_span_ids_to_sections(self):
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

    def test_compile_chapter_parts_happy_path(self, tmp_path):
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

    def test_process_chapter_single_chapter_file(self, tmp_path, capsys):
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
        result = process_chapter((test_env / 'ch01.html'), test_env, test_out)
        # first item is the intro file, so let's check on the first "chapter"
        assert os.path.exists(test_out / 'ch01.html')
        # check on return
        assert "ch01.html" in result

    def test_chapter_promote_headings(self, tmp_path, caplog):
        """
        we expect to have a single h1 and then a bunch of h2s
        in a single-file chapter, but we need to promote all the headings
        up on level for htmlbook to process them correctly
        """
        with open(tmp_path / 'ch.html', 'wt') as f:
            f.write("""<section class="tex2jax_ignore mathjax_ignore"
id="this-is-another-subheading">
<h1>This is a chapter heading</h1>
<p>Along with some content… lovely.</p>
<section id="subsection">
<h2>Subsection
<a class="headerlink" href="#subsection" title="Permalink to this headline">
#</a></h2>
<p>Of course, we need to test subsections…</p>
<section id="another-subsection">
<h3>Another Subsection
<a class="headerlink" href="#-subsection" title="Permalink to this headline">
#</a></h3>
<p>And sub-sub sections…</p>
<section id="yes-another">
<h4>Yes, Another
<a class="headerlink" href="#yes-another" title="Permalink to this headline">
#</a></h4>
<p>And sub-sub-sub sections…</p>
<section id="id1">
<h5>Yes, Another
<a class="headerlink" href="#id1" title="Permalink to this headline">#</a></h5>
<p>And sub-sub-sub-sub sections…</p>
<section id="another">
<h6>A level that shouldn't be</h6>
<p>Text</p>
</section>
</section></section></section></section>
<section id="summary">
<h2>Summary
<a class="headerlink" href="#summary" title="Permalink to this headline">#</a>
</h2>
<p>Finally, a summary.</p></section></section>""")
        result = process_chapter_single_file(tmp_path / 'ch.html')[0]
        assert str(result) == """<section data-type="chapter" id="this""" + \
                              """-is-another-subheading" xmlns="http:/""" + \
                              """/www.w3.org/1999/xhtml">
<h1>This is a chapter heading</h1>
<p>Along with some content… lovely.</p>
<section id="subsection">
<h1>Subsection
<a class="headerlink" href="#subsection" title="Permalink to this headline">
#</a></h1>
<p>Of course, we need to test subsections…</p>
<section id="another-subsection">
<h2>Another Subsection
<a class="headerlink" href="#-subsection" title="Permalink to this headline">
#</a></h2>
<p>And sub-sub sections…</p>
<section id="yes-another">
<h3>Yes, Another
<a class="headerlink" href="#yes-another" title="Permalink to this headline">
#</a></h3>
<p>And sub-sub-sub sections…</p>
<section id="id1">
<h4>Yes, Another
<a class="headerlink" href="#id1" title="Permalink to this headline">#</a></h4>
<p>And sub-sub-sub-sub sections…</p>
<section id="another">
<h5>A level that shouldn't be</h5>
<p>Text</p>
</section>
</section></section></section></section>
<section id="summary">
<h1>Summary
<a class="headerlink" href="#summary" title="Permalink to this headline">#</a>
</h1>
<p>Finally, a summary.</p></section></section>"""

    def test_process_chapter_filepaths(self, tmp_path):
        """
        ensure the returned/written filepath is correct
        also includes testing nested directories
        """
        test_env = tmp_path / 'tmp'
        test_out = test_env / 'output'
        test_env.mkdir()
        test_out.mkdir()
        shutil.copytree('tests/example_book/_build/html',
                        test_env, dirs_exist_ok=True)
        shutil.copytree(test_env / 'notebooks',
                        test_env / 'chapters/notebooks')
        result = process_chapter((test_env / 'notebooks/ch01.html'),
                                 test_env, test_out)[0]
        result += process_chapter((test_env / 'chapters/notebooks/ch01.html'),
                                  test_env, test_out)[0]
        # first item is the intro file, so let's check on the first "chapter"
        assert os.path.exists(test_out / 'notebooks/ch01.html')
        assert os.path.exists(test_out / 'chapters/notebooks/ch01.html')
        # check on return
        assert "notebooks/ch01.html" in result
        assert "chapters/" in result

    def test_process_chapter_with_subfiles(self, tmp_path):
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
            ], test_env, test_out)[0]
        # first item is the intro file, so let's check on the first "chapter"
        # the resulting section should have a data-type of "chapter"
        assert "ch02" in result
        assert os.path.exists(test_out / 'ch02.00.html')

    def test_process_chapter_with_subsections(self, tmp_path, capsys):
        """
        ensure subsections are getting data-typed appropriately
        """
        test_env = tmp_path / 'tmp'
        test_out = test_env / 'output'
        test_env.mkdir()
        test_out.mkdir()
        shutil.copytree('tests/example_book/_build/html/notebooks',
                        test_env, dirs_exist_ok=True)
        process_chapter([
            test_env / 'ch02.00.html',
            test_env / 'ch02.01.html',
            test_env / 'ch02.02.html',
            ], test_env, test_out)

        with open(test_out / 'ch02.00.html') as f:
            text = f.read()
            assert 'data-type="sect1"' in text
            assert 'data-type="sect2"' in text
            assert 'data-type="sect3"' in text
            assert 'data-type="sect4"' in text
            assert 'data-type="sect5"' in text

    def test_process_chapter_no_section(self, tmp_path):
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
        process_chapter(tmp_path / 'nosection.html', tmp_path, test_out)
        # the resulting section should have a data-type of "chapter"
        with open(test_out / 'nosection.html') as f:
            text = f.read()
            assert text.find('xmlns="http://www.w3.org/1999/xhtml"') > -1

    def test_process_chapter_totally_invalid_file(self, tmp_path, caplog):
        """
        if we ever try to process something that's super malformed, don't,
        and alert the user
        """
        with open(tmp_path / 'malformed.html', 'wt') as f:
            f.write("""<div>
    <h1>Hello!</h1>
</div>""")
        # first item is the intro file, so let's check on the first "chapter"
        result = process_chapter(tmp_path / 'malformed.html', tmp_path)
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
    def test_process_chapter_guessing_datatypes(self, tmp_path, datatype):
        """
        happy path for guessing datatypes, i.e, they're allowed
        """
        test_env = tmp_path / 'tmp'
        test_out = test_env / 'output'
        test_env.mkdir()
        test_out.mkdir()
        test_file_path = test_env / f'{datatype}.html'
        shutil.copy('tests/example_book/_build/html/intro.html',
                    test_file_path)
        process_chapter(test_file_path, test_env, test_out)
        # the resulting section should have a data-type of "datatype"
        with open(test_out / f'{datatype}.html') as f:
            text = f.read()
            assert text.find(f'data-type="{datatype}') > -1

    @pytest.mark.parametrize(
            "datatype", [
                "preface",
                "colophon"
                ]
            )
    def test_process_chapter_guessing_datatypes_in_path(
                                                        self,
                                                        tmp_path,
                                                        datatype
                                                       ):
        """
        Test about guessing datatypes, which can happen even if there is other
        stuff in the file name, e.g., 00- and so on.
        """
        test_env = tmp_path / 'tmp'
        test_out = test_env / 'output'
        test_env.mkdir()
        test_out.mkdir()
        test_file_path = test_env / f'00-{datatype}.html'
        shutil.copy('tests/example_book/_build/html/intro.html',
                    test_file_path)
        process_chapter(test_file_path, test_env, test_out)
        # the resulting section should have a data-type of "datatype"
        # but retain its filename
        with open(test_out / f'00-{datatype}.html') as f:
            text = f.read()
            assert text.find(f'data-type="{datatype}') > -1

    @pytest.mark.parametrize(
            "datatype", [
                ("prereqs", "preface"),
                ("author_bio", "afterword")
                ]
            )
    def test_process_chapter_guessing_datatypes_inferred(
                                                        self,
                                                        tmp_path,
                                                        datatype
            ):
        """
        confirm that the default front/backmatter data types are applied
        in the case that we get an inferred front/backmatter chapter title
        """
        test_env = tmp_path / 'tmp'
        test_out = test_env / 'build'
        test_env.mkdir()
        test_out.mkdir()
        test_file_path = test_env / f'{datatype[0]}.html'
        shutil.copy('tests/example_book/_build/html/intro.html',
                    test_file_path)
        process_chapter(test_file_path, test_env, test_out)
        # the resulting section should have a data-type of "datatype"
        with open(test_out / f'{datatype[0]}.html') as f:
            text = f.read()
            assert text.find(f'data-type="{datatype[1]}') > -1
