import logging
import os
import pytest
import shutil
from typer.testing import CliRunner
from jupyter_book_to_htmlbook.main import app, __version__

runner = CliRunner()


class TestMain:
    """
    Suite of tests for main loop and CLI functionality
    """

    def test_show_version(self):
        """ confirm that the version option works """
        result = runner.invoke(app, ["--version"])
        assert __version__ in result.stdout

    @pytest.mark.jb
    @pytest.mark.slow
    def test_simple_case(self,
                         tmp_path,
                         monkeypatch: pytest.MonkeyPatch,
                         caplog):
        """ happy path test case """
        # setup
        caplog.set_level(logging.DEBUG)
        test_env = tmp_path / 'tmp'
        test_env.mkdir()
        shutil.copytree('tests/example_book', test_env, dirs_exist_ok=True)
        monkeypatch.chdir(tmp_path)  # patch for our build target

        # run
        result = runner.invoke(app, [str(test_env), 'build'])
        log = caplog.text
        assert result.exit_code == 0
        assert "jupyter-book run" in log
        assert 'build/intro.html' in result.stdout
        assert os.path.exists(tmp_path / 'build')
        assert os.path.isfile(tmp_path / 'build/intro.html')
        with open(tmp_path / 'build/notebooks.html', 'rt') as f:
            assert 'data-type="chapter"' in f.read()

    @pytest.mark.jb
    @pytest.mark.slow
    def test_simple_case_with_json(self,
                                   tmp_path,
                                   monkeypatch: pytest.MonkeyPatch,
                                   caplog):
        """ happy path test case, NOW WITH ATLAS.JSON! """
        # setup
        caplog.set_level(logging.DEBUG)
        test_env = tmp_path / 'tmp'
        test_env.mkdir()
        shutil.copytree('tests/example_book', test_env, dirs_exist_ok=True)
        shutil.copyfile('tests/example_json/atlas.json',
                        tmp_path / 'atlas.json')
        monkeypatch.chdir(tmp_path)  # patch for our build target
        atlas = tmp_path / 'atlas.json'

        # run
        result = runner.invoke(app, [str(test_env), 'build',
                                     '--atlas-json', atlas])
        log = caplog.text
        assert result.exit_code == 0
        assert "Updated atlas.json" in log
        with atlas.open() as f:
            assert 'build/notebooks.html' in f.read()
