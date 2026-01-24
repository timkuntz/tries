import pytest

from less.cli import main


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        (["index", "/tmp"], "Indexing PDFs under: /tmp"),
        (["search", "demo query"], "Searching for: demo query"),
    ],
)
def test_cli_commands(args, expected, capsys):
    exit_code = main(args)
    captured = capsys.readouterr()

    assert exit_code == 0
    assert expected in captured.out
