"""Download PDF files from arXiv."""
import os
import tempfile
import arxiv
from typing import Optional, Tuple


def download_arxiv_pdf(arxiv_id: str, output_dir: Optional[str] = None) -> Tuple[str, dict]:
    """
    Download a PDF from arXiv by paper ID.
    
    Args:
        arxiv_id: The arXiv paper ID (e.g., '1706.03762' or 'cs.CV/2301.12345')
        output_dir: Directory to save the PDF. If None, uses a temporary directory.
    
    Returns:
        Tuple of (pdf_path, metadata_dict) where metadata contains:
            - title: Paper title
            - authors: List of authors
            - summary: Abstract
            - entry_id: Full arXiv ID
    """
    # Normalize arXiv ID (remove category prefix if present for download)
    clean_id = arxiv_id.split('/')[-1] if '/' in arxiv_id else arxiv_id
    
    # Create output directory if needed
    if output_dir is None:
        output_dir = tempfile.mkdtemp()
    os.makedirs(output_dir, exist_ok=True)
    
    # Download using arxiv library
    client = arxiv.Client()
    search = arxiv.Search(id_list=[clean_id])
    results = list(client.results(search))
    
    if not results:
        raise ValueError(f"Paper with ID {arxiv_id} not found on arXiv")
    
    paper = results[0]
    
    # Download PDF
    pdf_filename = f"{clean_id}.pdf"
    pdf_path = os.path.join(output_dir, pdf_filename)
    paper.download_pdf(dirpath=output_dir, filename=pdf_filename)
    
    # Extract metadata
    metadata = {
        'title': paper.title,
        'authors': [str(author) for author in paper.authors],
        'summary': paper.summary,
        'entry_id': paper.entry_id,
        'published': paper.published.isoformat() if paper.published else None,
    }
    
    return pdf_path, metadata

