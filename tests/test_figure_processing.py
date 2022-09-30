from pathlib import Path
from bs4 import BeautifulSoup as Soup  # type: ignore
from jupyter_book_to_htmlbook.figure_processing import (
        process_figures,
        process_informal_figs
)


class TestFigureProcessing:
    """
    Tests around figure processing
    """

    def test_simple_figure_case(self):
        """ simple case based on a simple figure """
        text = """<figure class="align-default" id="example-fig">
<a class="reference internal image-reference" href="images/flower.png">
<img alt="images/flower.png" src="../_images/flower.png"
style="height: 150px;" /></a>
<figcaption>
<p><span class="caption-number">Fig. 1 </span><span class="caption-text">
Here is my figure caption!</span>
<a class="headerlink" href="#example-fig" title="Permalink to this image">#</a>
</p></figcaption>"""
        chapter = Soup(text, 'html.parser')
        result = process_figures(chapter, Path('example'))
        assert str(result) == """<figure class="align-default" id="example-fig">

<img alt="images/flower.png" src="../_images/flower.png"/>
<figcaption>
<p><span class="caption-text">
Here is my figure caption!</span>

</p></figcaption></figure>"""

    def test_markdown_figure_case(self):
        """ support "markdown figure" syntax in jupyter-book """
        text = """<figure class="align-default" id="md-fig">
<a class="remove-me reference internal image-reference"
href="images/flower.png">
<img alt="flower" class="remove-me" src="_images/flower.png"
style="width: 200px; height: 200px;" /></a>
<figcaption>
<p><span class="caption-number">Fig. 2 </span>
<span class="caption-text">And here is a <em>markdown</em> caption</span>
<a class="headerlink" href="#markdown-fig" title="Permalink to this image">
#</a></p></figcaption></figure>"""
        chapter = Soup(text, 'html.parser')
        result = process_figures(chapter, Path('example'))
        assert str(result) == """<figure class="align-default" id="md-fig">

<img alt="flower" class="remove-me" src="_images/flower.png"/>
<figcaption>
<p>
<span class="caption-text">And here is a <em>markdown</em> caption</span>
</p></figcaption></figure>"""

    def test_markdown_image(self):
        """ support bare markdown images, i.e., informal figs """
        text = '<p><img alt="Flower" src="../_images/flower.png" /></p>'
        chapter = Soup(text, 'html.parser')
        result = process_informal_figs(chapter, Path('example'))
        assert str(result) == (
            '<figure class="informal"><img alt="Flower" ' +
            'src="../_images/flower.png"/></figure>')

    def test_myst_image(self):
        """ support myst bare image markup """
        text = '<a class="some-class reference internal image-reference" ' + \
               'href="images/flower.png"><img alt="flower" class="som' + \
               'e-class align-center" src="_images/flower.png" style="' + \
               'width: 249px; height: 150px;" /></a>'
        chapter = Soup(text, 'html.parser')
        result = process_informal_figs(chapter, Path('example'))
        assert str(result) == (
            '<figure class="informal"><img alt="flower" ' +
            'src="_images/flower.png"/></figure>')

    # edge cases
    def test_no_anchor_wrap(self):
        """
        What happens if, unexpectly, there isn't an anchor wrap?

        The figure should still convert as expected.
        """
        text = """<figure class="align-default" id="md-fig">
<img alt="flower" class="remove-me" src="_images/flower.png"
style="width: 200px; height: 200px;" />
<figcaption>
<p><span class="caption-number">Fig. 2 </span>
<span class="caption-text">And here is a <em>markdown</em> caption</span>
<a class="headerlink" href="#markdown-fig" title="Permalink to this image">
#</a></p></figcaption></figure>"""
        chapter = Soup(text, 'html.parser')
        result = process_figures(chapter, Path('example'))
        assert str(result) == """<figure class="align-default" id="md-fig">
<img alt="flower" class="remove-me" src="_images/flower.png"/>
<figcaption>
<p>
<span class="caption-text">And here is a <em>markdown</em> caption</span>
</p></figcaption></figure>"""

    def test_no_caption_number(self):
        """
        What happens if there isn't a caption number?

        (We should still convert correctly)
        """
        text = """<figure class="align-default" id="example-fig">
<a class="reference internal image-reference" href="images/flower.png">
<img alt="images/flower.png" src="_images/flower.png"
style="height: 150px;" /></a>
<figcaption>
<p><span class="caption-text">
Here is my figure caption!</span>
<a class="headerlink" href="#example-fig" title="Permalink to this image">#</a>
</p></figcaption>"""
        chapter = Soup(text, 'html.parser')
        result = process_figures(chapter, Path('example'))
        assert str(result) == """<figure class="align-default" id="example-fig">

<img alt="images/flower.png" src="_images/flower.png"/>
<figcaption>
<p><span class="caption-text">
Here is my figure caption!</span>

</p></figcaption></figure>"""
