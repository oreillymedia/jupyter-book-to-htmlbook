def process_figures(chapter):
    """
    Takes a chapter soup and handles changing the references to figures
    to the /images directory per usual htmlbook repo
    """
    figures = chapter.find_all(class_="figure")
    for figure in figures:
        # change div to figure tag
        figure.name = 'figure'

        # clean anything extraneous, if extant
        if figure.find_all('a', class_="headerlink") != []:
            for anchor in figure.find_all('a', class_="headerlink"):
                anchor.decompose()

        # get img tag out of any surrounding a tags
        try:
            figure.a.unwrap()
        except AttributeError:
            pass

        # remove any styles on the img tag
        del figure.img['style']

        # update uri
        img_tag = figure.find('img')
        uri = img_tag['src']
        img_fn = uri.split('/')[-1]
        img_tag['src'] = f'images/{img_fn}'

        # update caption
        caption = figure.find(class_='caption')
        caption.name = 'figcaption'
        # remove numbering if extant
        if caption.find(class_="caption-number"):
            numbering = caption.find(class_='caption-number')
            numbering.decompose()
    return chapter


def process_informal_figs(chapter):
    """
    This should be run *AFTER* process figs, but basically just repoints the
    img tags.
    """
    for img in chapter.find_all('img'):
        uri = img['src']
        img_fn = uri.split('/')[-1]
        img['src'] = f'images/{img_fn}'
    return chapter
