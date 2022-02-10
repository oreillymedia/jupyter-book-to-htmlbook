from typing import Type
from bs4 import BeautifulSoup # type: ignore
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
    chapter.name = 'section'
    chapter['data-type'] = 'chapter'
    chapter['xmlns'] = 'http://www.w3.org/1999/xhtml'
    del chapter['class']
    # add class="pagenumrestart" if it's the first chapter (will need to be changed for parts, but -- will handle that later)
    if base_chapter_file.find('/01/') > -1 or base_chapter_file.find('/1/') > -1:
        chapter['class'] = "pagenumrestart"
    # update chapter id to what is actually referred to (as far as I can tell)
    try:
        id_span = chapter.find('span')
        chapter['id'] = id_span['id']
        id_span.decompose()
    except KeyError:
        pass # this isn't an issue
        # print(f'Unable to move span id in {base_chapter_file}. This may not be a problem.')
    except TypeError as e:
        print(f'Error: {e} in {base_chapter_file}')
    except ValueError as e:
        print(f'Error: {e} in {base_chapter_file}')

 
    # work with subfiles
    for subfile in ordered_chapter_files_list[1:]:
        with open(subfile, 'r') as f:
            soup = BeautifulSoup(f, 'html.parser')
            section = soup.find(class_='section')
            section.name = 'section'
            section['data-type'] = 'sect1'
            del section['class']
            # deal with subsections
            subsections = section.find_all(class_="section")
            for sub in subsections:
                if sub.select('div > h2'):
                    sub.name = 'section'
                    sub['data-type'] = 'sect2'
                    # parsing subsections within seems like the best stragegy...
                elif sub.select('div > h3'):
                    sub.name = 'section'
                    sub['data-type'] = 'sect3'
                elif sub.select('div > h4'):
                    sub.name = 'section'
                    sub['data-type'] = 'sect4'
                elif sub.select('div > h5'):
                    sub.name = 'section'
                    sub['data-type'] = 'sect5'
            # add section to chapter
            chapter.append(section)

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
    if rm_numbering == True:
        for span in chapter.find_all(class_="section-number"):
            span.decompose()

    # remove any heading links
    for link in chapter.find_all(class_="headerlink"):
        link.decompose()
    return chapter


def process_figures(chapter):
    """
    Takes a chapter soup and handles changing the references to figures
    to the /images directory per usual htmlbook repo
    """
    figures = chapter.find_all(class_="figure")
    for figure in figures:
        # change div to figure tag
        figure.name = 'figure'

        # update uri
        img_tag = figure.find('img')
        uri = img_tag['src']
        img_fn = uri.split('/')[-1] 
        img_tag['src'] = f'images/{img_fn}'

        # update caption
        caption = figure.find(class_='caption')
        caption.name = 'figcaption'
        # remove numbering
        numbering = caption.find(class_='caption-number')
        numbering.decompose()
        # handle apparently common edge case!
        if img_tag.find('figcaption'):
            # extract the caption and move it to the figure tag
            caption.extract()
            figure.append(caption)
            # clear contents of the img tag (self closes it)
            img_tag.clear()
    return chapter
        

def process_informal_figs(chapter):
    """
    This should be run *AFTER* process figs, but basically just repoints the 
    img tags.
    """
    for img in chapter.find_all('img'):
        uri = img['src']
        img_fn = uri.split('/')[-1] 
        img['src'] = f'images/{img_fn}'
    return chapter


def process_interal_refs(chapter):
    """
    Processes internal a tags with "reference internal" classes.
    Converts bib references into spans (to deal with later), and other
    refernces to valid htmlbook xrefs. Currently opinionated towards CMS 
    author-date.
    """
    xrefs = chapter.find_all(class_='internal')
    for ref in xrefs:
        # handle bib references, be opinionated!
        if ref['href'].find('references.html') > -1:
            ref.name = 'span'
            del(ref['href'])
            # remove any interal tags
            inner_str = ''
            for part in ref.contents:
                inner_str += part.string
            # remove last comma per CMS
            inner_str = ','.join(inner_str.split(',')[0:-1]) + inner_str.split(',')[-1]
            ref.string = f' ({inner_str})' # need the space because these were footnotes
            # remove parent brackets
            parent = ref.parent
            parent.contents = ref
        else: # i.e., non reference xrefs
            ref['data-type'] = 'xref'
            uri = ref['href'] # get current uri and fix it if needed
            uri = uri.split('#')[-1]
            ref.string = f'#{uri}'
            ref['href'] = f'#{uri}'
    return chapter

def process_footnotes(chapter):
    """
    Takes footnote anchors and footnote lists and turns them into 
    <span data-type='footnote'> tags.
    """
    footnote_refs = chapter.find_all(class_='footnote-reference')
    # move the contents of the ref to the anchor point
    for ref in footnote_refs:
        try:
            #<a class="footnote-reference brackets" href="#psql" id="id3">1</a>
            ref_id = ref['href'].split('#')[-1]
            # double next_sibling b/c next sigling is a space
            ref_location = chapter.find("dt", {"id": ref_id}).next_sibling.next_sibling
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
        pass # no index in this chapter
    return chapter

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
            except AttributeError: # i.e., there is markup inside the thing
                title.name = 'h1'
            
    return chapter

def process_math(chapter):
    """
    Takes latex math notation and applies HTMLBook-compliant metadata such that
    it can be displayed when converted.
    """
    maths = chapter.find_all(class_="math")
    for eq in maths: # assume latex
        eq['data-type'] = "tex"
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

def process_chapter(toc_element):
    """
    Takes a list of chapter files and chapter lists and then writes the chapter to the root directory in which the script is run. Note that this is predicated on the files being in some /html/ directory or some such
    """

    # list of front and back matter guessed-at filenames
    front_matter = ['preface', 'notation', 'prereqs', 'titlepage', 'foreword', 'introduction']
    back_matter = ['colophon', 'author_bio', 'references', "acknowledgments", "conclusion", "afterword"]
    # data-types
    allowed_data_types = ["colophon", "halftitlepage", "titlepage", "copyright-page", "dedication", "acknowledgments", "afterword", "conclusion", 'foreword', 'introduction', 'preface']

    if isinstance(toc_element, str): # single-file chapter
        # this should really be a function, but for now
        ch_name = toc_element.split('.')[0].split('/')[-1]
        with open(toc_element, 'r') as f:
            base_soup = BeautifulSoup(f, 'html.parser')

        # perform initial swapping and namespace designation
        chapter = base_soup.find(class_='section') 
        chapter.name = 'section'
        chapter['xmlns'] = 'http://www.w3.org/1999/xhtml'
        
        # apply appropriate data-type (best guess)
        if ch_name.lower() in front_matter:
            if ch_name.lower() in allowed_data_types:
                chapter['data-type'] = ch_name.lower()
            else:
                chapter['data-type'] = "preface"
        elif ch_name.lower() in back_matter:
            if ch_name.lower() in allowed_data_types:
                chapter['data-type'] = ch_name.lower()
            else:
                chapter['data-type'] = "afterword"
        else:
            chapter['data-type'] = 'chapter'
        del chapter['class']
        
        # update chapter id to what is actually referred to (as far as I can tell)
        try:
            id_span = chapter.find('span')
            chapter['id'] = id_span['id']
            id_span.decompose()
        except KeyError as e:
            print(f'Unable to move span id in {toc_element}. This may not be a problem.\n{e}')
        except TypeError as e:
            print(f'Unable to move span id in {toc_element}. This may not be a problem.\n{e}')
    else: # i.e., an ordered list of chapter parts
        chapter = compile_chapter_parts(toc_element)
        ch_name = 'ch' + toc_element[0].split('/')[-2]
        
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
    with open(f'{ch_name}.html', 'w') as f:
        f.write(str(chapter))
