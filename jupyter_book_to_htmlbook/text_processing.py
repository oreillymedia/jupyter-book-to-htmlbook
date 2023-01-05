import re


def clean_chapter(chapter, rm_numbering=True):
    """
    "Cleans" the chapter from any script or style tags, removes table borders,
    removes any style attrs, and by default removes any section numbering.
    """
    remove_tags = ['style', 'script']
    all_tags = chapter.find_all()
    for tag in all_tags:
        if tag.name in remove_tags:
            tag.decompose()
        if tag.name == 'table':
            del tag['border']
    for tag in chapter.find_all(attrs={'style': True}):
        del tag['style']

    # (optionally) remove numbering
    if rm_numbering:
        for span in chapter.find_all(class_="section-number"):
            span.decompose()

    classes_to_remove = [
        # remove hidden cells. in the web version, these cells are hidden by
        # default and users can toggle them on/off. but they take up too much
        # space if rendered into the pdf.
        ".tag_hide-input > .cell_input",
        ".tag_hide-output > .cell_output",
        ".tag_hide-cell",
        ".toggle-details",

        # remove any heading links
        ".headerlink",
    ]

    for el in chapter.select(','.join(classes_to_remove)):
        el.decompose()
    return chapter


def move_span_ids_to_sections(chapter):
    """
    Takes empty span tags under a section parent with a heading next sibling
    and moves the id to the parent section tag so Atlas can find the cross
    reference.
    """
    empty_id_spans = chapter.find_all("span", id=True, string="")
    for span in empty_id_spans:
        if (
                span.parent.name == "section" and
                span.next_sibling.name in ["h1", "h2", "h3", "h4", "h5"]
           ):
            # add span id to section
            span.parent['id'] = span['id']
            # remove the now unneeded span
            span.decompose()
    return chapter


def process_sidebars(chapter):
    """
    Sidebars should be tagged with appropriate datatype and
    should have the correct heading level (h5)
    """
    sidebars = chapter.find_all("aside", class_="sidebar")

    for aside in sidebars:
        aside["data-type"] = "sidebar"

        if aside.find("p", class_="sidebar-title"):
            title = aside.find("p", class_="sidebar-title")
            title.name = "h5"

    return chapter
