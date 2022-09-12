import shutil
import os
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

    def test_simple_case(self, tmp_path):
        """ happy path test case """
        test_env = tmp_path / 'tmp'
        test_env.mkdir()
        shutil.copytree('tests/example_html', test_env, dirs_exist_ok=True)
        result = runner.invoke(app, [str(test_env), str(test_env / 'build')])
        assert result.exit_code == 0
        assert os.path.exists(test_env / 'build')
        assert os.path.isfile(test_env / 'build/ch01.html')
        with open(test_env / 'build/ch01.html') as f:
            assert 'data-type="chapter"' in f.read()
