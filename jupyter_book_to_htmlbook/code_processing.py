def process_code(chapter):
    """
    Turn rendered <pre> blocks into appropriately marked-up HTMLBook
    """

    highlight_divs = chapter.find_all(class_="highlight")

    for div in highlight_divs:
        parent_classes = str(div.parent["class"])
        pre_tag = div.pre
        pre_tag["data-type"] = "programlisting"

        # remove existing span classes
        for span in pre_tag.find_all('span'):
            del span['class']

        # add language info if available
        if "python" in parent_classes:
            pre_tag["data-code-language"] = "python"

    return chapter
