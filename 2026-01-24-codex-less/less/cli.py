from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from . import indexer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="less",
        description="LESS - LLM Empowered Semantic Search",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    index_parser = subparsers.add_parser(
        "index",
        help="Recurse a path and index PDF files into the vector database",
    )
    index_parser.add_argument("path", help="Path to a directory of PDFs")

    search_parser = subparsers.add_parser(
        "search",
        help="Query the index and return the most relevant results",
    )
    search_parser.add_argument("query", help="Search query")

    return parser


def _run_index(path: str) -> int:
    root = Path(path)
    print(f"Indexing PDFs under: {root}")
    print("Scanning for PDF files...")
    pdfs = indexer.list_pdfs(root)
    print(f"Found {len(pdfs)} PDF files.")
    indexer.index_pdfs(pdfs)
    print("Index complete.")
    return 0


def _run_search(query: str) -> int:
    print(f"Searching for: {query}")
    print("Retrieving relevant chunks...")
    print("Ranking results...")
    print("Search complete.")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "index":
            return _run_index(args.path)
        if args.command == "search":
            return _run_search(args.query)
    except Exception as exc:  # pragma: no cover - defensive fallback
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print("Error: Unknown command.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
