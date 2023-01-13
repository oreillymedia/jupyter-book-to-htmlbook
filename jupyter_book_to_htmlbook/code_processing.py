import re
import logging
from bs4 import NavigableString  # type: ignore
from .helpers import base_soup


def process_code(chapter, skip_numbering=False):
    """
    Turn rendered <pre> blocks into appropriately marked-up HTMLBook
    """

    cell_number = 0
    highlight_divs = chapter.find_all(class_="highlight")

    for div in highlight_divs:
        try:
            parent_classes = str(div.parent.get("class"))

            # apply `data-type` attribute
            pre_tag = div.pre
            pre_tag["data-type"] = "programlisting"

            # remove existing span classes
            for span in pre_tag.find_all('span'):
                del span['class']
                # clean up empty strings
                if not span.string:
                    # Log message in advance of any unanticipated edge case
                    logging.info(f"Removing empty span {span} in process_code")
                    span.decompose()

            # add language info if available
            if (  # handle R, use `find` for `%%` since we only want it if it's
                  # the very first span tag
                    pre_tag.find('span', string="%%") and
                    pre_tag.find_all('span', string="R")
               ):
                pre_tag["data-code-language"] = "r"
                # remove possibly confusing parent classes
                del div.parent['class']
                # remove extraneous rpy2 flags on first element (thus "find")
                pre_tag.find('span', string="%%").decompose()
                pre_tag.find('span', string="R").decompose()
                # remove left space/extra newline on first child element
                if pre_tag.contents:
                    start_code = pre_tag.contents[0]
                    pre_tag.contents[0].replace_with(start_code.lstrip())

            # handle python
            elif "python" in parent_classes:
                pre_tag["data-code-language"] = "python"

            # apply numbering
            if not skip_numbering:
                cell_number = number_codeblock(pre_tag, cell_number)

        except TypeError:
            logging.warning(f"Unable to apply cell numbering to {div}")

    return chapter


def number_codeblock(pre_block, cell_number):
    """
    Adds numbering markers (`In [##]: ` or `Out[##]: `) to cell blocks

    Note that BeautifulSoup modifies elements in place, so instead of
    returning the pre_block element, we're only returning the cell_number
    to be used in subsequent cells.
    """

    # grandparent of highlight div contains in/out information
    grandparent = pre_block.parent.parent.parent

    if "cell_input" in str(grandparent.get("class")):
        in_block = True
        cell_number += 1
        marker = f"In [{cell_number}]: "
    elif (
            "cell_output" in grandparent.get("class") and
            # ensure we're not in a hidden-input cell
            "tag_hide-input" not in grandparent.parent.get("class")
         ):
        in_block = False
        marker = f"Out[{cell_number}]: "
    else:
        return cell_number

    # insert marker
    pre_block.insert(0, marker)

    # calculate additional indent
    indent = ' ' * len(marker)

    # update tab alignment
    for index, element in enumerate(pre_block.contents):
        if type(element) == NavigableString:
            if re.search(r'\n\s*', element):
                indented_code = element.replace('\n', f'\n{indent}')
                # remove unneeded blank space b/t two newlines for
                # cleanliness (and to keep old tests passing)
                indented_code = indented_code.replace(f'\n{indent}\n', '\n\n')
                # the index-replace contortions are required by the
                # vagaries of modifying NavigableString.
                pre_block.contents[index].replace_with(indented_code)
            elif not in_block:
                # out blocks won't have spans put into them willy-nilly
                # so a "brute force" approach to indentation works fine
                element.replace_with(element.replace('\n', f'\n{indent}'))

    return cell_number


def process_code_examples(chapter):
    """
    Applies appropriate data types and adds titles for formal code
    "Examples" in the text
    """
    examples = chapter.find_all("div", class_="tag_example")

    for example_cell in examples:
        pre_block = example_cell.find("pre")
        comments = pre_block.find_all("span", class_="c1")

        if (  # it's an R block
                (pre_block.find("span", class_="o", string="%%") ==
                    pre_block.find_all("span")[1]) and
                (pre_block.find("span", class_="k", string="R") ==
                    pre_block.find_all("span")[2])
           ):
            example_name, example_title = example_get_name_and_title_r(
                                                                 pre_block)

        elif len(comments) < 2 or not (  # it's malformed
                comments[0] in pre_block.find_all("span")[0:3] and
                comments[1] in pre_block.find_all("span")[0:3]
               ):
            logging.warning(
                "Missing first two line comments for uuid and title." +
                f"Unable to apply example formatting to {example_cell}.")
            return chapter

        # ensure comments are within the first three spans (since we
        # expect an empty span to start based on their highlighter)
        else:  # we're getting what we expect
            example_name, example_title = example_get_name_and_title(comments)
            # remove empty space left by decomposed spans
            # assuming they add the empty span at the beginning of block
            for element in pre_block.contents[0:3]:
                if (
                        type(element) == NavigableString and
                        element.string in ["\n", "\n\n"]
                   ):
                    element.replace_with('')

            logging.info("Applying example formatting to and removing" +
                         f" first comments from: {example_cell}")

        if example_name is not None and example_title is not None:
            # apply data-type to cell (gets us including output for free)
            example_cell["data-type"] = "example"
            example_cell["id"] = example_name

            # add an h5 tag with the appropriate heading
            soup = base_soup(example_cell)
            heading = soup.new_tag("h5")
            example_cell.insert(0, heading)
            # have to have the tag in the tree before adding the title
            heading.append(example_title)

    return chapter


def example_get_name_and_title(comments):
    """
    In a code "example," this function extracts the
    name and title based on the first two comments
    """
    # first comment should be uuid/name; only take first word if many
    # to preserve id attribute validation
    example_name = comments[0].string
    example_name = example_name.split(" ")[1]  # remove comment "# "
    comments[0].decompose()
    # second comment should be the example title
    example_title = comments[1].string
    example_title = " ".join(example_title.split(" ")[1:])
    comments[1].decompose()

    return example_name, example_title


def example_get_name_and_title_r(pre_block):
    """
    Pulls and removes name and title information from R blocks.
    """
    # first three elements will be spans letting us know it's an R block
    r_code = pre_block.contents[3]
    expected_comments = r'# (.*?)\n# (.*?)\n## R'
    id_and_title = re.search(expected_comments, r_code)
    try:
        example_name = id_and_title.group(1)
        example_title = id_and_title.group(2)
        new_r_code = re.sub(expected_comments, "## R", r_code)
        pre_block.contents[3].replace_with(new_r_code)
        return example_name, example_title
    except (IndexError, AttributeError) as error:
        logging.warning(
            "Missing first two line comments for uuid and title." +
            f"Unable to apply example formatting: {error}.")
        return None, None
