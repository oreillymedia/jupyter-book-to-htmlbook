from bs4 import BeautifulSoup
from jupyter_book_to_htmlbook.figure_processing import process_figures, process_informal_figs


def test_process_figures_order_agnostic():
    """
    Confirm that divs with figure classes are appropriately converted
    into htmlbook figures. This should be processing-order agnostic, i.e.,
    some of what's in here may be ripped out by other functions (e.g.,
    clean_chapter(), but this should convert properly either way.
    """
    chapter_text = """<div class="figure align-default" id="example">
<a class="reference internal image-reference" href="../../_images/example.jpg">
<img alt="../../_images/example.jpg" src="../../_images/example.jpg"
style="width: 375.0px; height: 500.0px;" /></a>
<p class="caption"><span class="caption-number">
Fig. 8.1 </span><span class="caption-text">An example image.
Here is another sentence.</span>
<a class="headerlink" href="#scorecard" title="Permalink to this image">¶</a>
</p>
</div>"""
    chapter = BeautifulSoup(chapter_text, 'html.parser')
    result = process_figures(chapter)
    assert str(result) == """<figure class="figure align-default" id="example">

<img alt="../../_images/example.jpg" src="images/example.jpg"/>
<figcaption class="caption"><span class="caption-text">An example image.
Here is another sentence.</span>

</figcaption>
</figure>"""


def test_process_figures_expected():
    """
    test conversion for what we'd actually expect at time of processing
    """
    chapter_text = """
<div class="figure align-default" id="example">
<a class="reference internal image-reference"
href="../../_images/example.jpg">
<img alt="../../_images/example.jpg" src="../../_images/example.jpg"/></a>
<p class="caption"><span class="caption-number">Fig. 8.1 </span>
<span class="caption-text">An example image.</span>
</p>
</div>"""
    chapter = BeautifulSoup(chapter_text, 'html.parser')
    result = process_figures(chapter)
    assert str(result) == """
<figure class="figure align-default" id="example">

<img alt="../../_images/example.jpg" src="images/example.jpg"/>
<figcaption class="caption">
<span class="caption-text">An example image.</span>
</figcaption>
</figure>"""


def test_process_figures_handle_no_a_wrapper():
    """
    ensure that we gracefully handle the case in which the img tag isn't
    wrapped by an a tag
    """
    chapter_text = """
<div class="figure align-default" id="example">
<img alt="../../_images/example.jpg" src="../../_images/example.jpg"/>
<p class="caption"><span class="caption-number">Fig. 8.1 </span>
<span class="caption-text">An example image.</span>
</p>
</div>"""
    chapter = BeautifulSoup(chapter_text, 'html.parser')
    result = process_figures(chapter)
    assert str(result) == """
<figure class="figure align-default" id="example">
<img alt="../../_images/example.jpg" src="images/example.jpg"/>
<figcaption class="caption">
<span class="caption-text">An example image.</span>
</figcaption>
</figure>"""


def test_informal_fig_processing():
    """ tests path fixes to floating img tags """
    chapter_text = "<img src='/path/to/some/image.png'>"
    chapter = BeautifulSoup(chapter_text, "html.parser")
    result = process_informal_figs(chapter)
    assert str(result) == '<img src="images/image.png"/>'
