import re
import logging
from bs4 import NavigableString  # type: ignore


def process_code(chapter):
    """
    Turn rendered <pre> blocks into appropriately marked-up HTMLBook
    """

    cell_number = 0
    highlight_divs = chapter.find_all(class_="highlight")

    # instead have to do this differently, += 1 on IN only
    for div in highlight_divs:
        try:
            # get parent and grandparent information
            parent_classes = str(div.parent["class"])
            grandparent = div.parent.parent
            logging.info(f"Code before: {div}")

            pre_tag = div.pre
            pre_tag["data-type"] = "programlisting"

            # apply numbering
            if "cell_input" in str(grandparent["class"]):
                cell_number += 1
                pre_tag = number_codeblock(pre_tag, cell_number)

            elif (
                    "cell_output" in grandparent["class"] and
                    # ensure we're not in a hidden-input cell
                    "tag_hide-input" not in grandparent.parent["class"]
                 ):
                # check to ensure the preceding in block isn't hidden
                pre_tag = number_codeblock(pre_tag,
                                           cell_number,
                                           in_block=False)

            # remove existing span classes
            for span in pre_tag.find_all('span'):
                del span['class']

            # add language info if available
            if "python" in parent_classes:
                pre_tag["data-code-language"] = "python"

            logging.info(f"Code after: {div}")

        except TypeError:
            logging.warning(f"Unable to apply cell numbering to {div}")

        except KeyError:
            logging.warning(f"Unable to apply cell numbering to {div}")

    return chapter


def number_codeblock(pre_block, cell_number, in_block=True):
    """
    Adds numbering markers (`In [##]: ` or `Out[##]: `) to cell blocks
    """
    if in_block:
        marker = f"In [{cell_number}]: "
    else:
        marker = f"Out[{cell_number}]: "

    # insert marker
    pre_block.insert(0, marker)

    # calculate additional indent
    indent = ' ' * len(marker)

    # update tab alignment
    for element in pre_block.contents:
        if type(element) == NavigableString:
            if re.match(r'\n\s*', element):
                element.insert_after(indent)
            elif not in_block:
                # out blocks won't have spans put into them willy-nilly
                # so a "brute force" approach to indentation works fine
                element.replace_with(element.replace('\n', f'\n{indent}'))

    return pre_block
