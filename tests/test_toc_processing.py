import shutil
from jupyter_book_to_htmlbook.toc_processing import get_book_index


def test_get_book_index_simple(tmp_path):
    """
    tests expected (happy) path reading a 'genindex.html' file
    and returning a list of chapter files
    """
    test_env = tmp_path / 'tmp'
    test_env.mkdir()
    shutil.copytree('tests/example-1', test_env, dirs_exist_ok=True)
    toc = get_book_index(test_env)
    assert type(toc) == list
    assert toc == [
            test_env / "landing-page.html",
            test_env / "00-Preface.html",
            test_env / "01-Introduction-To-World.html",
            test_env / "02-Experiments-and-Stats-Review.html"
            ]


def test_get_book_index_with_sub_chapter_files(tmp_path):
    """
    tests expected (happy) path reading a 'genindex.html' file
    and returning a list of chapter files (which in this case are sometimes
    lists of subchapter files)
    """
    test_env = tmp_path / 'tmp'
    test_env.mkdir()
    shutil.copytree('tests/example-2', test_env, dirs_exist_ok=True)
    toc = get_book_index(test_env)
    assert type(toc) == list
    assert toc == [
                    test_env / 'preface.html',
                    test_env / 'prereqs.html',
                    test_env / 'notation.html',
                    [
                        test_env / 'ch/01/lifecycle_intro.html',
                        test_env / 'ch/01/lifecycle_question.html',
                        test_env / 'ch/01/lifecycle_obtain.html',
                        test_env / 'ch/01/lifecycle_data.html',
                        test_env / 'ch/01/lifecycle_world.html',
                        test_env / 'ch/01/lifecycle_map.html'
                    ],
                    [
                        test_env / 'ch/02/data_scope_intro.html',
                        test_env / 'ch/02/data_scope_big_data_hubris.html',
                        test_env / 'ch/02/data_scope_construct.html',
                        test_env / 'ch/02/data_scope_protocols.html',
                        test_env / 'ch/02/data_scope_natural.html',
                        test_env / 'ch/02/data_scope_accuracy.html',
                        test_env / 'ch/02/data_scope_summary.html',
                        test_env / 'ch/02/data_scope_exercises.html'
                    ],
                    test_env / 'references.html'
                  ]
