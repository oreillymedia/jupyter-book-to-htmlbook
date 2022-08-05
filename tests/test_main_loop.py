import shutil
import os
from jupyter_book_to_htmlbook.jupter_book_to_htmlbook import main


def test_main_loop_happy_path(tmp_path):
    """ happy path for an admittedly quick n' dirty integration """
    test_env = tmp_path / 'tmp'
    test_env.mkdir()
    shutil.copytree('tests/example_html', test_env, dirs_exist_ok=True)
    main(test_env / 'html', test_env / 'build')
    assert os.path.exists(test_env / 'build')
    assert os.path.isfile(test_env / 'build/ch01.html')
    with open(test_env / 'build/ch01.html') as f:
        assert 'data-type="chapter"' in f.read()
