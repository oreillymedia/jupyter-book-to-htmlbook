from bs4 import BeautifulSoup  # type: ignore
from jupyter_book_to_htmlbook.math_processing import process_math


def test_process_math_divs():
    """
    Test for latex math notation and apply HTMLBook-compliant metadata so
    it can be displayed when converted, i.e., add 'data-type="tex"'

    Divs should be wrapped with equation data-type divs.
    """
    chapter_content = r"""<div class="math notranslate nohighlight">
\[
\begin{aligned}
\mathbf{X} &amp;= \mathbf{U} \mathbf{\Sigma} \mathbf{V^\top}
\end{aligned}
\]</div>"""
    chapter = BeautifulSoup(chapter_content, 'html.parser')
    result = process_math(chapter)
    assert str(result) == r"""<div data-type="equation">""" + \
                          r"""<div class="math notransla""" + \
                          r"""te nohighlight" data-type="tex">
\[
\begin{aligned}
\mathbf{X} &amp;= \mathbf{U} \mathbf{\Sigma} \mathbf{V^\top}
\end{aligned}
\]</div></div>"""


def test_process_math_spans():
    """
    Test for latex math notation and apply HTMLBook-compliant metadata so
    it can be displayed when converted, i.e., add 'data-type="tex"'
    """
    chapter_content = r"""<p>see
<span class="math">\(D\)</span> as well as
<span class="math">\(T\)</span> to show the
example.</p>"""
    chapter = BeautifulSoup(chapter_content, 'html.parser')
    result = process_math(chapter)
    assert str(result) == r"""<p>see
<span class="math" data-type="tex">\(D\)</span> as well as
<span class="math" data-type="tex">\(T\)</span> to show the
example.</p>"""
