from bs4 import NavigableString  # type: ignore


def process_figures(chapter):
    """
    Takes a chapter soup and handles changing the references to figures
    to the /images directory per usual htmlbook repo
    """
    figures = chapter.find_all("figure")
    for figure in figures:
        # clean anything extraneous, if extant
        if figure.find_all('a', class_="headerlink") != []:
            for anchor in figure.find_all('a', class_="headerlink"):
                anchor.decompose()

        # get img tag out of any surrounding a tags
        try:
            figure.a.unwrap()
        except AttributeError:
            pass  # i.e., no surrounding anchor tag

        # remove any styles on the img tag
        del figure.img['style']

        # remove any caption numbering
        caption_number = figure.find(class_='caption-number')
        try:
            caption_number.decompose()
        except AttributeError:
            pass  # i.e., no caption numbering

        # clean up the figure caption
        caption_text = figure.find("span", class_="caption-text")
        if figure.find("figcaption"):
            figure.find("figcaption").replace_with(caption_text)
            caption_text.name = "figcaption"
            if type(caption_text.contents[0]) == NavigableString:
                caption_text.contents[0].replace_with(
                        caption_text.contents[0].string.lstrip())

    return chapter


def process_informal_figs(chapter):
    """
    This should be run *AFTER* process figs, but basically just repoints the
    img tags.
    """
    for img in chapter.find_all('img'):
        # Since, weirdly, a myst-marked image will be in a floating anchor
        if img.parent.name == 'a':
            img.parent.name = "figure"
            img.parent['class'] = "informal"
            del img.parent['href']

        # if it's in a paragraph all by itself, make informal fig
        if img.parent.name == 'p' and len(img.parent.contents) == 1:
            img.parent.name = 'figure'
            img.parent['class'] = 'informal'

        # strip out any classes, styles, etc. on the image
        del img['class']
        del img['style']

    return chapter
