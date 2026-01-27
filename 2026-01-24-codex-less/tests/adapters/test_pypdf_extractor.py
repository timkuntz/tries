from pathlib import Path

from less.adapters.pypdf_extractor import PypdfExtractor


def test_pypdf_extractor_reads_pdf_pages():
    pdf_path = Path(__file__).parents[1] / "ai-companies.pdf"

    extractor = PypdfExtractor()
    pages = extractor.extract_pages(pdf_path)

    assert pages
    assert any("OpenAI" in page for page in pages)
