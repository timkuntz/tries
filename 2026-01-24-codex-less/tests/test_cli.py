import pytest

from less import cli


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        (["index", "/tmp"], "Indexing PDFs under: /tmp"),
        (["search", "demo query"], "Searching for: demo query"),
    ],
)
def test_cli_commands(args, expected, capsys):
    exit_code = cli.main(args)
    captured = capsys.readouterr()

    assert exit_code == 0
    assert expected in captured.out

