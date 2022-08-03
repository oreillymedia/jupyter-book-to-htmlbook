from pathlib import Path
from bs4 import BeautifulSoup  # type: ignore
from admonition_processing import process_admonitions
from figure_processing import process_figures, process_informal_figs
from footnote_processing import process_footnotes
from math_processing import process_math
from xref_processing import process_interal_refs
import re


def compile_chapter_parts(ordered_chapter_files_list):
    """
    Takes a list of chapter file URIs and returns a basic, sectioned
    chapter soup (i.e., with no other htmlbook optimizations)
    """
    # work with main file
    base_chapter_file = ordered_chapter_files_list[0]
    with open(base_chapter_file, 'r') as f:
        base_soup = BeautifulSoup(f, 'html.parser')
    chapter = base_soup.find(class_='section')
    chapter.name = 'section'  # type: ignore
    chapter['data-type'] = 'chapter'  # type: ignore
    chapter['xmlns'] = 'http://www.w3.org/1999/xhtml'  # type: ignore
    del chapter['class']  # type: ignore
    # add class="pagenumrestart" if it's the first chapter
    # (will need to be changed for parts, but -- will handle that later)
    if base_chapter_file.find('/01/') > -1 or \
       base_chapter_file.find('/1/') > -1:
        chapter['class'] = "pagenumrestart"  # type: ignore
    # update chapter id to what is actually referred to (as far as I can tell)
    err_feel_better_msg = "It's possible there is no empty span here " + \
                          "and likely is not a problem."

    try:
        id_span = chapter.find('span')  # type: ignore
        chapter['id'] = id_span['id']  # type: ignore
        id_span.decompose()  # type: ignore

    except TypeError as e:
        print(f'Error: {e} in {base_chapter_file}\n{err_feel_better_msg}')
    except ValueError as e:
        print(f'Error: {e} in {base_chapter_file}\n{err_feel_better_msg}')

    # work with subfiles
    for subfile in ordered_chapter_files_list[1:]:
        with open(subfile, 'r') as f:
            soup = BeautifulSoup(f, 'html.parser')
            section = soup.find(class_='section')
            section.name = 'section'  # type: ignore
            section['data-type'] = 'sect1'  # type: ignore
            del section['class']  # type: ignore
            # move id from empty span to section
            try:
                section['id'] = section.select_one('span')['id']  # type: ignore
                # leave spans for now in case they're not empty;
                # TO DO: clean up empty spans...
                del section.select_one('span')['id']  # type: ignore
            except KeyError:
                pass  # like before, if it's not there that's OK.
            # deal with subsections
            subsections = section.find_all(class_="section")  # type: ignore
            for sub in subsections:
                # remove duplicate sub-section summary ids
                # (do chapter-level stuff with post-processing scripts
                # b/c those handle in-chapter xrefs better)
                if sub['id'] == "summary":
                    sub['id'] = f"{subfile.split('/')[-1].split('.')[0]}_summary"
                if sub.select('div > h2'):
                    sub.name = 'section'
                    sub['data-type'] = 'sect2'
                    # parsing subsections within seems like the best strategy
                elif sub.select('div > h3'):
                    sub.name = 'section'
                    sub['data-type'] = 'sect3'
                elif sub.select('div > h4'):
                    sub.name = 'section'
                    sub['data-type'] = 'sect4'
                elif sub.select('div > h5'):
                    sub.name = 'section'
                    sub['data-type'] = 'sect5'
            # if the subfile has a "summary" section, add subfile name to
            # summary id
            # NOTE: xrefs to summaries will not work! will handle this when
            # it comes up...
            # add section to chapter
            chapter.append(section)  # type: ignore

    return chapter


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
            del(tag['border'])
    for tag in chapter.find_all(attrs={'style': True}):
        del tag['style']
    # (optinally) remove numbering

    if rm_numbering:
        for span in chapter.find_all(class_="section-number"):
            span.decompose()

    tags_to_remove = [
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

    for el in chapter.select(','.join(tags_to_remove)):
        el.decompose()
    return chapter


def move_span_ids_to_sections(chapter):
    """
    Takes span tags with "sec-" ids and moves the id to the next heading tag
    so Atlas can find the cross reference.
    """
    sec_spans = chapter.find_all("span", id=re.compile('sec-*'))
    for span in sec_spans:
        # get id
        span_id = span['id']
        # get next heading
        section = span.find_parent('section')
        # add span id to section
        section['id'] = span_id
        # remove span so no dup ids
        span.decompose()
    return chapter


def process_chapter(toc_element, build_dir=Path('.')):
    """
    Takes a list of chapter files and chapter lists and then writes the chapter
    to the root directory in which the script is run. Note that this assumes
    that the files are in some /html/ directory or some such
    """

    # list of front and back matter guessed-at filenames
    front_matter = ['preface', 'notation', 'prereqs',
                    'titlepage', 'foreword', 'introduction']
    back_matter = ['colophon', 'author_bio', 'references',
                   "acknowledgments", "conclusion", "afterword"]
    # data-types
    allowed_data_types = ["colophon", "halftitlepage", "titlepage",
                          "copyright-page", "dedication", "acknowledgments",
                          "afterword", "conclusion", 'foreword',
                          'introduction', 'preface']

    if isinstance(toc_element, str):  # single-file chapter
        # this should really be a function, but for now
        ch_name = toc_element.split('.')[0].split('/')[-1]
        with open(toc_element, 'r') as f:
            base_soup = BeautifulSoup(f, 'html.parser')

        # perform initial swapping and namespace designation
        try:
            chapter = base_soup.find(class_='section')
            chapter.name = 'section'  # type: ignore
            chapter['xmlns'] = 'http://www.w3.org/1999/xhtml'  # type: ignore

        except AttributeError:  # does not have a section class for top-level
            if base_soup.main:
                chapter = base_soup.main.section
                chapter['xmlns'] = 'http://www.w3.org/1999/xhtml'  # type: ignore
            else:  # this is an edge case, and I'm going to leave it for now
                return

        # apply appropriate data-type (best guess)
        if ch_name.lower() in front_matter:
            if ch_name.lower() in allowed_data_types:
                chapter['data-type'] = ch_name.lower()  # type: ignore
            else:
                chapter['data-type'] = "preface"  # type: ignore
        elif ch_name.lower() in back_matter:
            if ch_name.lower() in allowed_data_types:
                chapter['data-type'] = ch_name.lower()  # type: ignore
            else:
                chapter['data-type'] = "afterword"  # type: ignore
        else:
            chapter['data-type'] = 'chapter'  # type: ignore
        del chapter['class']  # type: ignore

        # update chapter id to what is actually referred to
        try:
            id_span = chapter.find('span')  # type: ignore
            chapter['id'] = id_span['id']  # type: ignore
            id_span.decompose()  # type: ignore
        except KeyError as e:
            print(f'Unable to move span id in {toc_element}. ' +
                  f'This may not be a problem.\n{e}')
        except TypeError as e:
            print(f'Unable to move span id in {toc_element}. ' +
                  f'This may not be a problem.\n{e}')
    else:  # i.e., an ordered list of chapter parts
        chapter = compile_chapter_parts(toc_element)
        ch_name = 'ch' + toc_element[0].split('/')[-2]

    # see where we're at
    print(f"Processing {ch_name}...")

    # perform cleans and processing
    chapter = clean_chapter(chapter)
    chapter = process_interal_refs(chapter)
    chapter = process_figures(chapter)
    chapter = process_informal_figs(chapter)
    chapter = process_footnotes(chapter)
    chapter = process_admonitions(chapter)
    chapter = process_math(chapter)
    chapter = move_span_ids_to_sections(chapter)

    # write the file
    out = build_dir / (ch_name + '.html')
    out.write_text(str(chapter))
