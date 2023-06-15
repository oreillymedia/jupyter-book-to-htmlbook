import pytest
from bs4 import BeautifulSoup  # type: ignore
from jupyter_book_to_htmlbook.text_processing import (
    clean_chapter,
    move_span_ids_to_sections,
    process_sidebars
    )


@pytest.mark.slow
def test_passthroughs(fresh_book_html):
    """
    Test around various markup and passthroughs, also meant to serve
    as a "smoke test" during future Jupyter Book version upgrades
    """
    with (fresh_book_html / "notebooks/markup.html").open("r") as f:
        chapter = f.read()
    soup = BeautifulSoup(chapter, "html.parser")
    clean_chapter(soup, False)

    # keep together
    assert soup.find("span", class_="keep-together")
    # note inside complex list
    assert soup.find("div",
                     attrs={
                            "data-type": "note"
                            }).parent.name == "li"  # type: ignore
    # section with pagebreak-before
    assert soup.find("section", attrs={"data-type": "sect2",
                                       "class": ["pagebreak-before",
                                                 "less-space"]})
    # bold in code passthrough
    assert soup.find("pre",
                     attrs={"data-type":
                            "programlisting"}).find("strong")  # type: ignore


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
</h2>"""
    chapter = BeautifulSoup(chapter_text, 'html.parser')
    result = clean_chapter(chapter)
    assert str(result) == """

<table>
<tr><td>Hello</td><td>World</td></tr>
</table>
<p>Lorem ipsum</p>
<h2>Issues with Linear Regression
</h2>"""


def test_chapter_cleans_table_specific():
    """
    A few table-specific edge cases to check, including a no-border table
    and tables with valign/width attributes
    """
    chapter = BeautifulSoup("""<table>
<tr halign="left">
<th rowspan="2" valign="top">0</th>
<td width="50%">NaN</td>
<td>NaN</td>
<td>NaN</td>
</tr>
</table>""", "html.parser")
    result = clean_chapter(chapter)
    halign_tr = result.find("tr")
    valign_th = result.find("th")
    width_td = result.find("td")  # it'll find the first
    assert not halign_tr.get("valign")  # type: ignore
    assert not valign_th.get("valign")  # type: ignore
    assert not width_td.get("width")  # type: ignore


def test_chapter_clean_table_caption():
    """
    Ensure that we are preserving the captions, but removing the caption
    numbering provided by Jupyter Book
    """
    chapter = BeautifulSoup("""
<table class="table" id="example-table">
<caption><span class="caption-number">Table 1 </span>
<span class="caption-text">Table title</span>
<a class="headerlink" href="#example-table" title="Permalink">#</a></caption>
<colgroup>
<col style="width: 50%" />
<col style="width: 50%" />
</colgroup><thead>
<tr class="row-odd"><th class="head"><p>Col1</p></th>
<th class="head"><p>Col2</p></th>
</tr></thead><tbody>
<tr class="row-odd"><td><p>Row2 under Col1</p></td>
<td><p>Row2 under Col2</p></td>
</tr></tbody></table>""", "html.parser")
    result = clean_chapter(chapter)
    assert not result.find("span", class_="caption-number")


def test_move_span_ids_to_sections():
    """
    Atlas requires that cross reference targets sections so that
    the links and cross-reference text will appear as expected in Atlas
    """
    chapter_text = """
<section data-type="chapter" id="analytics" xmlns="http://w3.org/1999/xhtml">
<span id="chp-1"></span><h1>Analytics</h1>
<section class="section" data-type="sect2" id="types-of-bias">
<span id="sec-biastypes"></span><h2>Types of Bias</h2>
<p>Bias <span id="donotmove"></span>comes in many forms!</p>
</section></section>"""
    chapter = BeautifulSoup(chapter_text, 'html.parser')
    result = move_span_ids_to_sections(chapter)
    sections = result.find_all("section")
    assert sections[0]["id"] == "chp-1"
    assert sections[1]["id"] == "sec-biastypes"
    assert not result.find("p", id=True)


def test_sidebar_processing():
    """
    Sidebars from jupyter book (from the ```{sidebar} syntax) are
    formatted as <aside>s with a "sidebar" class. For HTMLBook, these
    need to have sidebar data-types, and the paragraph with the
    "sidebar-title" class should be an <h5> element.
    """
    chapter_text = BeautifulSoup("""<aside class="sidebar">
<p class="sidebar-title">Here Is a Sidebar Title</p>
<p>And this is some sidebar content!</p>
</div>
</aside>""", "html.parser")
    process_sidebars(chapter_text)
    assert chapter_text.find("aside")["data-type"] == "sidebar"  # type: ignore
    assert chapter_text.find(
            "h1").string == "Here Is a Sidebar Title"  # type: ignore


def test_hidden_input_is_removed():
    """
    Ensure that our hidden content is removed when the "hide" class is present
    """
    chapter_text = BeautifulSoup("""
<div class="cell tag_hide-input docutils container">
<details class="hide above-input">
<summary aria-label="Toggle hidden content">
<span class="collapsed">Show code cell source</span>
<span class="expanded">Hide code cell source</span>
</summary>
<div class="cell_input docutils container">
<div class="highlight-ipython3 notranslate">
<div class="highlight">
<pre><span></span><span class="nb">print</span>""" +
                                 """<span class="p">(</span><span """ +
                                 """class="s2">&quot;The source """ +
                                 """for this his hidden!&quot;</span>""" +
                                 """<span class="p">)</span>
</pre></div>
</div>
</div>
</details>
<div class="cell_output docutils container">
<div class="output stream highlight-myst-ansi notranslate">
<div class="highlight"><pre><span></span>The source for this his hidden!
</pre></div>
</div>
</div>
</div>""", "html.parser")
    clean_chapter(chapter_text, False)
    assert not chapter_text.find("details")
    assert not chapter_text.find("div", class_="highlight-ipython3")


def test_hidden_output_is_removed():
    chapter_text = BeautifulSoup(
        """
<div class="cell tag_hide-output docutils container">
<div class="cell_input above-output-prompt docutils container">
<div class="highlight-ipython3 notranslate"><div class="highlight">
<pre><span></span><span class="nb">print</span>""" +
        """<span class="p">(</span><span class="s2">&quot;""" +
        """Don&#39;t see me!&quot;</span><span class="p">)</span>
</pre></div>
</div>
</div>
<details class="hide below-input">
<summary aria-label="Toggle hidden content">
<span class="collapsed">Show code cell output</span>
<span class="expanded">Hide code cell output</span>
</summary>
<div class="cell_output docutils container">
<div class="output stream highlight-myst-ansi notranslate">
<div class="highlight"><pre><span></span>Don&#39;t see me!
</pre></div>
</div>
</div>
</details>
</div>""", "html.parser")
    clean_chapter(chapter_text, False)
    assert not chapter_text.find("details")
    assert not chapter_text.find("div", class_="output")
