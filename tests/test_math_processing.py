from bs4 import BeautifulSoup
from jupyter_book_to_htmlbook.math_processing import process_math


def test_process_math():
    """
    Test for latex math notation and apply HTMLBook-compliant metadata so
    it can be displayed when converted, i.e., add 'data-type="tex"'
    """
    chapter_content = r"""<div class="math notranslate nohighlight">
\[
\begin{aligned}
\mathbf{X} &amp;= \mathbf{U} \mathbf{\Sigma} \mathbf{V^\top}
\end{aligned}
\]</div>"""
    chapter = BeautifulSoup(chapter_content, 'html.parser')
    result = process_math(chapter)
    assert str(result) == r"""<div class="math notranslate nohighlight" data-type="tex">
\[
\begin{aligned}
\mathbf{X} &amp;= \mathbf{U} \mathbf{\Sigma} \mathbf{V^\top}
\end{aligned}
\]</div>"""
