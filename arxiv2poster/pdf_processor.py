"""Extract and process information from PDF files."""
import re
from typing import Dict, Optional


def extract_paper_info(pdf_path: str, metadata: Dict) -> Dict[str, str]:
    """
    Extract key information from PDF for poster generation.
    
    Args:
        pdf_path: Path to the PDF file
        metadata: Metadata dictionary from arxiv downloader
    
    Returns:
        Dictionary with:
            - title: Paper title
            - abstract: Paper abstract/summary
            - key_concepts: Extracted key concepts (simplified for now)
    """
    # For now, use metadata directly
    # In the future, this could parse the PDF to extract more detailed information
    title = metadata.get('title', '')
    abstract = metadata.get('summary', '')
    
    # Extract key concepts from abstract (simple keyword extraction)
    # This is a simplified version - could be enhanced with NLP
    key_concepts = extract_key_concepts(abstract)
    
    return {
        'title': title,
        'abstract': abstract[:1000],  # Limit abstract length for prompt
        'key_concepts': key_concepts,
        'authors': ', '.join(metadata.get('authors', [])[:3]),  # First 3 authors
    }


def extract_key_concepts(text: str, max_concepts: int = 5) -> str:
    """
    Extract key concepts from text (simplified version).
    
    Args:
        text: Text to extract concepts from
        max_concepts: Maximum number of concepts to return
    
    Returns:
        Comma-separated string of key concepts
    """
    # Simple approach: look for capitalized phrases and technical terms
    # This is a placeholder - could be enhanced with proper NLP
    words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
    
    # Filter out common words and get unique concepts
    common_words = {'The', 'This', 'We', 'Our', 'These', 'That', 'In', 'On', 'At', 'For', 'With'}
    concepts = [w for w in words if w not in common_words and len(w) > 3]
    unique_concepts = list(dict.fromkeys(concepts))[:max_concepts]  # Preserve order, remove duplicates
    
    return ', '.join(unique_concepts) if unique_concepts else "Research, Machine Learning, Deep Learning"

