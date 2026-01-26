# LESS - LLM Empowered Semantic Search

## Summary

LESS is a command line tool with just two commands.

1. `index` is a command that accepts a path and will recurse the path and index PDF files into the vector database.
2. `search` is a command that accepts a query and will return the most relevant results.

* When a command is executed, the application should provide clear step-by-step feedback about what it is doing.
* It should report any errors that occur.
* It should exit cleanly in either a success or error scenario.

## Change Log

- 2026-01-24: Added `AGENTS.md` with project-specific agent guidance.
- 2026-01-24: Expanded testing guidance in `AGENTS.md` for Python projects.
- 2026-01-24: Created project `README.md` with setup and usage notes.
- 2026-01-24: Added `less` CLI entrypoint and basic CLI scaffolding with tests.
- 2026-01-24: Added `bin/less` bash wrapper for running the CLI.
- 2026-01-24: Added `.gitignore` for typical Python and tooling artifacts.
- 2026-01-24: Added PDF discovery and indexing plumbing with a CLI test.
- 2026-01-24: Split indexer logic and tests into dedicated modules.
- 2026-01-24: Added PDF text extraction with indexer test coverage.
- 2026-01-24: Added sentence-aware chunking with max/target sizing.
- 2026-01-24: Deferred spaCy import and added chunking tests with a fake NLP.
- 2026-01-24: Adjusted chunking to honor a 500-char minimum and 2000-char maximum.
- 2026-01-24: Added Chroma storage pipeline and sentence-transformer embedding integration.
- 2026-01-24: Updated Chroma dependencies and error guidance for runtime imports.
- 2026-01-24: Lowered Python requirement to 3.13 for chromadb/onnxruntime support.
- 2026-01-24: Enabled uv packaging config and setuptools build system for scripts.
