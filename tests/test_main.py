import tempfile
from typer.testing import CliRunner
from pathlib import Path
from vorlagellm.main import app
from unittest.mock import patch

from .test_tei import TEST_DOC, TEST_APPARATUS

def my_get_llm(*args, **kwargs):
    def my_llm(prompt):
        return "1"
    
    my_llm.bind = lambda *args, **kwargs: my_llm

    return my_llm


@patch('llmloader.load', my_get_llm)
def test_main_run():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdirname:
        output = Path(tmpdirname)/"test-apparatus.xml"
        result = runner.invoke(app, [
            "run",
            str(TEST_DOC),
            str(TEST_APPARATUS),
            str(output),
        ])
        
        assert result.exit_code == 0
        output_text = output.read_text()
        assert '<rdg wit="Treg NA28 #51">' in output_text
