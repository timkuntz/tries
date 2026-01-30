from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from .adapters import chromadb_store, filesystem, pypdf_extractor, spacy_chunker
from .adapters.sentence_transformer_embedder import SentenceTransformerEmbedder
from .core.use_cases import IndexDirectoryUseCase, IndexPdfUseCase, SearchUseCase


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


def build_index_use_case() -> IndexDirectoryUseCase:
    extractor = pypdf_extractor.PypdfExtractor()
    chunker = spacy_chunker.SpacySentenceChunker(min_chars=500, max_chars=2000)
    embedder = SentenceTransformerEmbedder()
    collection = chromadb_store.get_collection(
        "less",
        persist_path=Path(".less/chroma"),
    )
    vector_store = chromadb_store.ChromaVectorStore(collection)
    pdf_use_case = IndexPdfUseCase(
        extractor,
        chunker,
        embedder,
        vector_store,
        min_chars=500,
        max_chars=2000,
    )
    return IndexDirectoryUseCase(pdf_use_case)


def build_search_use_case() -> SearchUseCase:
    embedder = SentenceTransformerEmbedder()
    collection = chromadb_store.get_collection(
        "less",
        persist_path=Path(".less/chroma"),
    )
    vector_store = chromadb_store.ChromaVectorStore(collection)
    return SearchUseCase(embedder, vector_store, top_k=5)


def _run_index(path: str) -> int:
    root = Path(path)
    print(f"Indexing PDFs under: {root}")
    print("Scanning for PDF files...")
    pdfs = filesystem.list_pdfs(root)
    print(f"Found {len(pdfs)} PDF files.")
    if not pdfs:
        print("Embedding and storing 0 chunks...")
        print("Index complete.")
        return 0

    index_use_case = build_index_use_case()
    stored = index_use_case.index_paths(pdfs)
    print(f"Embedding and storing {stored} chunks...")
    print("Index complete.")
    return 0


def _run_search(query: str) -> int:
    print(f"Searching for: {query}")
    print("Embedding query...")
    search_use_case = build_search_use_case()
    print("Querying vector store...")
    results = search_use_case.search(query)
    print(f"Found {len(results)} results.")
    for index, result in enumerate(results, start=1):
        source = result.metadata.get("pdf_name", "unknown")
        page = result.metadata.get("page_number", "?")
        print(f"{index}. {source} (page {page}) score={result.score:.4f}")
        print(result.text)
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
