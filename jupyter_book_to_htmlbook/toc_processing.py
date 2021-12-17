from bs4 import BeautifulSoup # type: ignore

def get_book_index(basedir: str) -> list:
    indexfile = basedir + 'genindex.html'
    bookfile_uris = []

    with open(indexfile, 'r') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    for link in soup.find_all('a'):
        uri = link.get('href')
        if not uri == None and not uri.find('://') > -1:
            bookfile_uris.append(f'{basedir}{uri}')
    # remove the index file
    bookfile_uris = bookfile_uris[1:]
    

    book_toc = []
    chapter_collection = []
    # combine chapters into ordered lists
    for file in bookfile_uris:
        # I am sure there is a better way, but
        if not file.find('/ch/') > -1: # i.e., not in a chapter folder
            book_toc.append(file)
        else: # i.e., in a chapter folder
            # if we're not in a chapter yet, start the chapter
            if len(chapter_collection) == 0:
                chapter_collection.append(file)
            # if we're in the same chapter, add the file
            elif file.split('/')[-2] == chapter_collection[0].split('/')[-2]:
                chapter_collection.append(file)
            else: # if we're in a new chapter
                # add the last chapter to the book_toc
                book_toc.append(chapter_collection)
                # clear out the collection, replace with next chapter intro file
                chapter_collection = [file]
    return book_toc

