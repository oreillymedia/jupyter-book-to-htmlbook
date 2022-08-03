def process_figures(chapter):
    """
    Takes a chapter soup and handles changing the references to figures
    to the /images directory per usual htmlbook repo
    """
    figures = chapter.find_all(class_="figure")
    for figure in figures:
        # change div to figure tag
        figure.name = 'figure'

        # update uri
        img_tag = figure.find('img')
        uri = img_tag['src']
        img_fn = uri.split('/')[-1]
        img_tag['src'] = f'images/{img_fn}'

        # update caption
        caption = figure.find(class_='caption')
        caption.name = 'figcaption'
        # remove numbering
        numbering = caption.find(class_='caption-number')
        numbering.decompose()
        # handle apparently common edge case!
        if img_tag.find('figcaption'):
            # extract the caption and move it to the figure tag
            caption.extract()
            figure.append(caption)
            # clear contents of the img tag (self closes it)
            img_tag.clear()
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
