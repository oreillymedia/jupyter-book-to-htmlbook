def base_soup(element):
    try:
        soup = [x for x in element.parents][-1]
    except IndexError:
        soup = element
    return soup
