def process_math(chapter):
    """
    Takes latex math notation and applies HTMLBook-compliant metadata such that
    it can be displayed when converted.
    """
    maths = chapter.find_all(class_="math")
    for eq in maths:  # assume latex
        eq['data-type'] = "tex"
        if eq.name == 'div':  # wrap divs as equations
            # we have to get the soup to make a new tag...
            # this will be slow depending on how far down the rabbit hole
            # the equation is
            soup = [x for x in eq.parents][-1]
            eq.wrap(soup.new_tag("div"))
            eq.parent["data-type"] = "equation"
    return chapter
