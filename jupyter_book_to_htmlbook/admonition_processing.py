def process_admonitions(chapter):
    """
    Process admonitions based on htmlbook admonition types
    """
    admonitions = chapter.find_all(class_="admonition")
    htmlbook_admonition_types = [
        "note",
        "warning",
        "tip",
        "caution",
        "important"
    ]
    for admn in admonitions:
        types = admn.get('class')
        for type in types:
            if type in htmlbook_admonition_types:
                admn['data-type'] = type
            else:
                admn['data-type'] = "note"
        del(admn['class'])
        if admn.find(class_="admonition-title"):
            title = admn.find(class_="admonition-title")
            try:
                if not title.string.lower() in htmlbook_admonition_types:
                    title.name = 'h1'
                else:
                    title.decompose()
            except AttributeError:
                # i.e., there is markup inside the thing
                title.name = 'h1'

    return chapter
