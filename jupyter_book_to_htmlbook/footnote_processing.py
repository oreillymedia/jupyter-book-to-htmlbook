import logging


def process_footnotes(chapter):
    """
    Takes footnote anchors and footnote lists and turns them into
    <span data-type='footnote'> tags.
    """
    footnote_refs = chapter.find_all(class_='footnote-reference')
    # move the contents of the ref to the anchor point
    for ref in footnote_refs:
        try:
            ref_id = ref.get('href').split('#')[-1]
            # double next_sibling b/c next sibling is a space
            ref_location = chapter.find(
                                        "dt", {"id": ref_id}
                                        ).next_sibling.next_sibling
            footnote_contents = ref_location.find('p').children
            ref.name = 'span'
            ref['data-type'] = 'footnote'
            del ref['href']
            del ref['class']
            del ref['id']
            ref.string = ''
            for child in footnote_contents:
                ref.append(child)

        except AttributeError:
            logging.warning(f'Error converting footnote "{ref}".')
    # remove the list of footnote contents
    hrs = chapter.find_all('hr', {'class': 'footnotes'})
    for hr in hrs:
        hr.decompose()
    dls = chapter.find_all('dl', {'class': 'footnote'})
    for dl in dls:
        dl.decompose()

    return chapter
