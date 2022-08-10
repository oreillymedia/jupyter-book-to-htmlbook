def process_math(chapter):
    """
    Takes latex math notation and applies HTMLBook-compliant metadata such that
    it can be displayed when converted.
    """
    maths = chapter.find_all(class_="math")
    for eq in maths:  # assume latex
        eq['data-type'] = "tex"
    return chapter
