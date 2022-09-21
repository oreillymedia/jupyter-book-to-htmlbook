import logging


def process_interal_refs(chapter):
    """
    Processes internal a tags with "reference internal" classes.
    Converts bib references into spans (to deal with later), and other
    references to valid htmlbook xrefs. Currently opinionated towards CMS
    author-date.
    """
    xrefs = chapter.find_all(class_='internal')
    for ref in xrefs:
        # handle bib references, be opinionated!
        if ref['href'].find('references.html') > -1:
            ref.name = 'span'
            del ref['href']
            # remove any internal tags
            inner_str = ''
            for part in ref.contents:
                inner_str += part.string
            # remove last comma per CMS
            inner_str = ','.join(inner_str.split(',')[0:-1]) + \
                        inner_str.split(',')[-1]
            ref.string = f'({inner_str})'
            # remove parent brackets
            parent = ref.parent
            parent.contents = ref
            # remove any id tags on the parent to avoid duplicates
            del parent['id']
        elif ref['href'].find('htt') > -1:
            logging.warning(f"External image reference: {ref['href']}")
        else:  # i.e., non reference xrefs
            ref['data-type'] = 'xref'
            uri = ref['href']  # get current uri and fix it if needed
            uri = uri.split('#')[-1]
            ref.string = f'#{uri}'
            ref['href'] = f'#{uri}'
    return chapter
