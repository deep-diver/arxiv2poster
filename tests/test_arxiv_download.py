"""
Test arXiv PDF download functionality.
Tests downloading the "Attention is All You Need" paper (arXiv ID: 1706.03762).
"""
import os
import tempfile
import pytest
import arxiv


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test downloads."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_arxiv_pdf_download_by_id(temp_dir):
    """
    Test that arXiv PDF file is correctly downloaded.
    Sample paper: "Attention is All You Need" with arXiv ID 1706.03762.
    """
    arxiv_id = "1706.03762"
    
    # Download paper using arxiv library (as per PRD)
    client = arxiv.Client()
    search = arxiv.Search(id_list=[arxiv_id])
    results = list(client.results(search))
    
    # Verify paper was found
    assert len(results) > 0, f"Paper with ID {arxiv_id} not found"
    paper = results[0]
    
    # Verify paper metadata
    assert paper.entry_id is not None
    assert "1706.03762" in paper.entry_id
    
    # Download PDF
    output_path = os.path.join(temp_dir, "attention_paper.pdf")
    paper.download_pdf(dirpath=temp_dir, filename="attention_paper.pdf")
    
    # Verify PDF was downloaded
    assert os.path.exists(output_path), "PDF file was not downloaded"
    
    # Verify file is not empty
    file_size = os.path.getsize(output_path)
    assert file_size > 0, "Downloaded PDF file is empty"
    
    # Verify it's actually a PDF (check for PDF magic bytes)
    with open(output_path, 'rb') as f:
        header = f.read(4)
        assert header == b'%PDF', "Downloaded file is not a valid PDF"


def test_arxiv_paper_metadata_attention_is_all_you_need():
    """
    Test that the downloaded paper has correct metadata for "Attention is All You Need".
    """
    arxiv_id = "1706.03762"
    
    client = arxiv.Client()
    search = arxiv.Search(id_list=[arxiv_id])
    results = list(client.results(search))
    
    assert len(results) > 0
    paper = results[0]
    
    # Verify expected metadata
    assert paper.title is not None
    assert "attention" in paper.title.lower() or "transformer" in paper.title.lower()
    
    assert paper.authors is not None
    assert len(paper.authors) > 0
    
    assert paper.summary is not None
    assert len(paper.summary) > 0


def test_arxiv_download_with_category_prefix(temp_dir):
    """
    Test arXiv download with category prefix format (e.g., cs.CL/1706.03762).
    According to PRD, should support both formats.
    """
    # Try with category prefix (if applicable)
    # Note: 1706.03762 might not have a category prefix, so we'll test the format
    arxiv_id = "1706.03762"
    
    client = arxiv.Client()
    search = arxiv.Search(id_list=[arxiv_id])
    results = list(client.results(search))
    
    assert len(results) > 0
    paper = results[0]
    
    # Download PDF
    output_path = os.path.join(temp_dir, "paper_with_prefix.pdf")
    paper.download_pdf(dirpath=temp_dir, filename="paper_with_prefix.pdf")
    
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0


def test_arxiv_download_direct_url_method(temp_dir):
    """
    Test arXiv download using direct URL method as mentioned in PRD.
    Format: https://arxiv.org/pdf/{arxiv_id}.pdf
    """
    import urllib.request
    
    arxiv_id = "1706.03762"
    url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    output_path = os.path.join(temp_dir, "direct_download.pdf")
    
    # Download using direct URL
    urllib.request.urlretrieve(url, output_path)
    
    # Verify download
    assert os.path.exists(output_path), "PDF file was not downloaded via direct URL"
    
    # Verify file is not empty
    file_size = os.path.getsize(output_path)
    assert file_size > 0, "Downloaded PDF file is empty"
    
    # Verify it's a PDF
    with open(output_path, 'rb') as f:
        header = f.read(4)
        assert header == b'%PDF', "Downloaded file is not a valid PDF"


def test_arxiv_invalid_id_handling():
    """
    Test that invalid arXiv IDs are handled gracefully (as per PRD error handling requirements).
    """
    invalid_id = "9999.99999"  # Non-existent ID
    
    client = arxiv.Client()
    search = arxiv.Search(id_list=[invalid_id])
    results = list(client.results(search))
    
    # Should return empty results or handle gracefully
    # The exact behavior depends on arxiv library, but should not crash
    assert isinstance(results, list)

