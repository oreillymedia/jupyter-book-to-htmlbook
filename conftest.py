import pytest
import shutil
import subprocess
from pathlib import Path


@pytest.fixture(scope="class")
def fresh_book_html(tmp_path_factory):
    """
    A fresh Jupyter Build (if possible) to do some markup checks
    """
    test_env = tmp_path_factory.mktemp("example_book_html")
    shutil.copytree('tests/example_book', test_env, dirs_exist_ok=True)
    # Run `jb build`j in the tmp_path
    build = subprocess.run(["jb", "build", test_env],
                           capture_output=True)

    if build.returncode != 0:
        return Path("tests/example_book/_build/html")
    else:
        return test_env / "_build/html"


@pytest.fixture()
def tmp_book_path(tmp_path):
    """
    Provides a copy of the example_book html jupyter book build
    for use in tests.
    """
    test_env = tmp_path / 'tmp'
    test_env.mkdir()
    shutil.copytree('tests/example_book/_build/html',
                    test_env, dirs_exist_ok=True)
    return test_env
