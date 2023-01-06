import copy
import logging
import random
from .helpers import base_soup


def process_interal_refs(chapter):
    """
    Processes internal a tags with "reference internal" classes.
    Converts bib references into spans (to deal with later), and other
    references to valid htmlbook xrefs. Currently opinionated towards CMS
    author-date.
    """
    xrefs = chapter.find_all("a", class_='internal')
    for ref in xrefs:
        # handle bib references
        if (
                ref.parent.name == "span" and
                ref.parent.contents[0] == "[" and
                ref.parent.contents[-1] == "]"
           ):
            ref.name = 'span'
            del ref['href']
            # remove any internal tags
            inner_str = ''
            for part in ref.contents:
                inner_str += part.string
            # remove last comma (before year/date) per CMS
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

    chapter_ids = [element['id'] for element in chapter.find_all(id=True)]
    return chapter, chapter_ids


def add_glossary_datatypes(chapter):
    """
    Adds appropriate data types to glossary definition lists and terms.

    (Assumes being called only on a "glossary.*" file)
    """

    # We need to get base soup for adding new tags; the IndexError handling
    # is to facilitate testing when there isn't a root "document" behind
    # the "chapter"
    soup = base_soup(chapter)

    glossary_lists = chapter.find_all("dl")
    for gloss in glossary_lists:
        gloss["data-type"] = "glossary"
        terms = gloss.find_all("dt")
        for term in terms:
            term["data-type"] = "glossterm"
            for element in term.contents:
                if element.name == "a" and "headerlink" in element["class"]:
                    element.decompose()

            # Wrap term string or elements in dfn tags per HTMLBook spec
            try:
                term.string.wrap(soup.new_tag("dfn"))
            except AttributeError:
                # there's no easy to wrap multiple things in bs4
                # so this is the workaround
                rebuilt_term = soup.new_tag("dt")
                rebuilt_term["data-type"] = "glossterm"
                rebuilt_term.append(soup.new_tag("dfn"))
                for child in term.contents:
                    # due to frustrating subtleties with the way bs4
                    # handles children, we need to make a copy here
                    rebuilt_term.dfn.append(copy.copy(child))
                term.replace_with(rebuilt_term)

        defs = gloss.find_all("dd")
        for defn in defs:
            defn["data-type"] = "glossdef"
    return chapter


def process_citations(chapter):
    """
    Process and handle bibliographical citations in a chapter
    """
    bib_lists = chapter.find_all("dl", class_="citation")
    for bib in bib_lists:
        bib.name = "ul"
        bib["class"] = "author-date"
        for dt in bib.find_all("dt"):
            dt.decompose()
        for dd in bib.find_all("dd"):
            dd.name = "li"
    return chapter
