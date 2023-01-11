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
        assert not result.find("figcaption").find("a", class_="headerlink")
        assert result.find("img").get("style") is None
        assert not result.find("span", class_="caption-number")
        assert not result.find("a", class_="image-reference")

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
        assert not result.find("figcaption").find("a", class_="headerlink")
        assert result.find("img").get("style") is None
        assert not result.find("span", class_="caption-number")
        assert not result.find("a", class_="image-reference")

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

    def test_extra_p_tags_and_spaces_are_removed_from_captions(self):
        """
        In order to render captions correctly, we should ensure
        that the <figcaption> contains only text, without any extraneous
        whitespace or <p> tags
        """
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
        caption = result.find("figcaption")
        assert not caption.p
        assert "\n" not in caption.string
        assert caption.string[0] != " "

    def test_markup_is_preserved_in_captions(self):
        """
        Any markup in a figure caption should be preserved, but there
        should be no left spacing or newlines still
        """
        text = """<figure class="align-default" id="example-fig">
<a class="reference internal image-reference" href="images/flower.png">
<img alt="images/flower.png" src="../_images/flower.png"
style="height: 150px;" /></a>
<figcaption>
<p><span class="caption-number">Fig. 1 </span><span class="caption-text">
Here is my <code>figure</code> caption!</span>
<a class="headerlink" href="#example-fig" title="Permalink to this image">#</a>
</p></figcaption>"""
        chapter = Soup(text, 'html.parser')
        result = process_figures(chapter, Path('example'))
        caption = result.find("figcaption")
        assert not caption.p
        assert caption.find("code")
        assert "\n" not in caption.contents[0]

    def test_markup_is_preserved_in_captions_at_beginning(self):
        """
        Any markup in a figure caption should be preserved, even
        if it's at the beginning, and that the spaces aren't weird
        because of it in the rest of the caption
        """
        text = """<figure class="align-default" id="example-fig">
<a class="reference internal image-reference" href="images/flower.png">
<img alt="images/flower.png" src="../_images/flower.png"
style="height: 150px;" /></a>
<figcaption>
<p><span class="caption-number">Fig. 1 </span><span class="caption-text">
<strong>Here</strong> is <em>my</em> figure caption!</span>
<a class="headerlink" href="#example-fig" title="Permalink to this image">#</a>
</p></figcaption>"""
        chapter = Soup(text, 'html.parser')
        result = process_figures(chapter, Path('example'))
        caption = result.find("figcaption")
        assert caption.find("strong")
        assert caption.find("em")
        assert caption.contents[2] == " is "
        assert caption.contents[4][0] == " "  # leading space is retained

    # edge cases
    def test_no_anchor_wrap(self):
        """
        What happens if, unexpectedly, there isn't an anchor wrap?

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
        assert result.find("figcaption")
        assert not result.find("figcaption").find("a", class_="headerlink")
        assert result.find("img").get("style") is None
        assert not result.find("span", class_="caption-number")

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
        assert result.find("figcaption")
        assert not result.find("figcaption").find("a", class_="headerlink")
        assert result.find("img").get("style") is None
        assert not result.find("span", class_="caption-number")
