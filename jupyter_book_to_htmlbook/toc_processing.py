from bs4 import BeautifulSoup
from pathlib import Path


def get_book_index(basedir: Path) -> list:
    """
    Takes the 'genindex' file from a Jupyter Book HTML site and returns a
    list of chapter URIs and lists of chapter URIs where there is more than one
    file per chapter.
    """
    indexfile = basedir / 'genindex.html'
    bookfile_uris = []

    with open(indexfile, 'r') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    for link in soup.find_all('a'):
        uri = link.get('href')
        if uri is not None and not uri.find('://') > -1:
            bookfile_uris.append(Path(f'{basedir}/{uri}'))
    # remove the index file
    bookfile_uris = bookfile_uris[1:]

    book_toc = []
    chapter_collection = []

    # combine chapters into ordered lists
    for file in bookfile_uris:
        if not str(file).find('/ch/') > -1:  # i.e., not in a chapter folder
            # if we're at the end of a chapter collection, add it
            if len(chapter_collection) != 0:
                book_toc.append(chapter_collection)
            # then add the next file
            book_toc.append(file)
        else:  # i.e., in a chapter folder
            # if we're not in a chapter yet, start the chapter
            if len(chapter_collection) == 0:
                chapter_collection.append(file)
            # if we're in the same chapter, add the file
            elif str(file).split('/')[-2] == (
                        str(chapter_collection[0]).split('/')[-2]
                    ):
                chapter_collection.append(file)
            else:  # if we're in a new chapter
                # add the last chapter to the book_toc
                book_toc.append(chapter_collection)
                # clear out the collection,
                # replace with next chapter intro file
                chapter_collection = [file]
    return book_toc
