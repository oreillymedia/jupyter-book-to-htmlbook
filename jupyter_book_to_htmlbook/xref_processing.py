import logging
import random


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


def process_ids(chapter, existing_ids=[]):
    """
    Checks a list of IDs against ids that are already being used in the
    book, and if a match is found, append a random number to the id and
    return the chapter along with the entire list of IDs in the chapter
    (so we can check them against the next chapter and so on)
    """
    tags_with_id = chapter.find_all(id=True)

    for tag in tags_with_id:
        uid = tag["id"]
        if uid in existing_ids:
            new_id = f"{uid}_{random.randint(1, 123456789)}"
            tag["id"] = new_id

            # update any links to the old ID
            xrefs = chapter.find_all(href=f"#{uid}")
            for ref in xrefs:
                ref['href'] = f"#{new_id}"

            # log the change
            logging.info(f"Duplicate ID \"{uid}\" changed to \"{new_id}\"")

    return chapter, chapter.find_all(id=True)
