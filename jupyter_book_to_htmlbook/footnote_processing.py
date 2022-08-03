def process_footnotes(chapter):
    """
    Takes footnote anchors and footnote lists and turns them into
    <span data-type='footnote'> tags.
    """
    footnote_refs = chapter.find_all(class_='footnote-reference')
    # move the contents of the ref to the anchor point
    for ref in footnote_refs:
        try:
            # <a class="footnote-reference brackets" href="#psql" id="id3">1</a>
            ref_id = ref['href'].split('#')[-1]
            # double next_sibling b/c next sigling is a space
            ref_location = chapter.find(
                                        "dt", {"id": ref_id}
                                        ).next_sibling.next_sibling
            footnote_contents = ref_location.find('p').children
            ref.name = 'span'
            ref['data-type'] = 'footnote'
            del(ref['href'])
            del(ref['class'])
            del(ref['id'])
            ref.string = ''
            for child in footnote_contents:
                ref.append(child)
        except ValueError as e:
            print(f'{e}')
    # remove the list of footnote contents
    try:
        hrs = chapter.find_all('hr', {'class': 'footnotes'})
        for hr in hrs:
            hr.decompose()
        dls = chapter.find_all('dl', {'class': 'footnote'})
        for dl in dls:
            dl.decompose()
    except AttributeError:
        print("No index in this chapter...")
    return chapter
