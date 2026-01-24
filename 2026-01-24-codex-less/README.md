# LESS - LLM Empowered Semantic Search

LESS is a small Python CLI (in progress) with two commands:

- `index`: recurse a path and index PDF files into a vector database
- `search`: query the index and return the most relevant results

The CLI will report step-by-step progress, surface errors, and exit cleanly.

## Requirements

- Python 3.14+

## Setup

Using `uv`:

```sh
uv sync
```

Using `pip`:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
```

## Usage

CLI entry points:

```sh
less index /path/to/pdfs
less search "your query"
./bin/less index /path/to/pdfs
./bin/less search "your query"
python -m less index /path/to/pdfs
python -m less search "your query"
python main.py index /path/to/pdfs
python main.py search "your query"
```

## Development

Run tests:

```sh
python -m pytest
```

## Notes

- If your environment cannot load large language models locally, make sure your runtime is configured accordingly before indexing or searching.
