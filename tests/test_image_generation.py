"""
Test image generation and saving via Gemini API according to PRD specifications.
"""
import os
import tempfile
import pytest
from pathlib import Path
from google import genai
from google.genai import types


@pytest.fixture
def api_key():
    """Get API key from environment variable."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY or GOOGLE_API_KEY environment variable not set")
    return api_key


@pytest.fixture
def gemini_client(api_key):
    """Create and return a Gemini client instance."""
    return genai.Client(api_key=api_key)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_image_is_generated_and_saved(gemini_client, temp_dir):
    """
    Test that image is successfully generated and saved via Gemini API usage from PRD.
    
    This test follows the PRD implementation example:
    1. Generate content with image
    2. Extract image from response parts
    3. Save image to file
    """
    # Test data
    paper_title = "Test Paper Title"
    paper_summary = "This is a test summary for poster generation"
    orientation = "landscape"
    aspect_ratio = "16:9" if orientation == "landscape" else "9:16"
    resolution = "1K"  # Use 1K for faster testing
    
    # Create prompt according to PRD
    poster_prompt = f"""
Create an academic poster for the research paper:
Title: {paper_title}
Summary: {paper_summary}

The poster should be visually appealing, include the title prominently,
and represent the key concepts of the research.
"""
    
    # Generate the poster image according to PRD
    response = gemini_client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=poster_prompt,
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE'],
            image_config=types.ImageConfig(
                aspectRatio=aspect_ratio,  # camelCase for initialization
                imageSize=resolution       # camelCase for initialization
            ),
        )
    )
    
    # Verify response
    assert response is not None
    assert hasattr(response, 'parts')
    
    # Extract and save image according to PRD example
    output_path = os.path.join(temp_dir, "test_poster.png")
    image_saved = False
    
    for part in response.parts:
        if image := part.as_image():
            image.save(output_path)
            image_saved = True
            break
    
    # Verify image was saved
    assert image_saved, "No image part found in response"
    assert os.path.exists(output_path), "Image file was not created"
    
    # Verify file is not empty
    file_size = os.path.getsize(output_path)
    assert file_size > 0, "Saved image file is empty"


def test_image_saved_with_landscape_orientation(gemini_client, temp_dir):
    """Test image generation and saving with landscape orientation (16:9)."""
    test_prompt = "Create a simple academic poster with title and summary"
    aspect_ratio = "16:9"
    resolution = "1K"
    
    response = gemini_client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=test_prompt,
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE'],
            image_config=types.ImageConfig(
                aspectRatio=aspect_ratio,  # camelCase for initialization
                imageSize=resolution       # camelCase for initialization
            ),
        )
    )
    
    output_path = os.path.join(temp_dir, "landscape_poster.png")
    image_saved = False
    
    for part in response.parts:
        if image := part.as_image():
            image.save(output_path)
            image_saved = True
            break
    
    assert image_saved
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0


def test_image_saved_with_portrait_orientation(gemini_client, temp_dir):
    """Test image generation and saving with portrait orientation (9:16)."""
    test_prompt = "Create a simple academic poster with title and summary"
    aspect_ratio = "9:16"
    resolution = "1K"
    
    response = gemini_client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=test_prompt,
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE'],
            image_config=types.ImageConfig(
                aspectRatio=aspect_ratio,  # camelCase for initialization
                imageSize=resolution       # camelCase for initialization
            ),
        )
    )
    
    output_path = os.path.join(temp_dir, "portrait_poster.png")
    image_saved = False
    
    for part in response.parts:
        if image := part.as_image():
            image.save(output_path)
            image_saved = True
            break
    
    assert image_saved
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0


def test_image_saved_with_different_resolutions(gemini_client, temp_dir):
    """Test image generation and saving with different resolutions (1K, 2K, 4K)."""
    test_prompt = "Create a simple test image"
    aspect_ratio = "16:9"
    
    for resolution in ["1K", "2K", "4K"]:
        response = gemini_client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=test_prompt,
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE'],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                    image_size=resolution
                ),
            )
        )
        
        output_path = os.path.join(temp_dir, f"poster_{resolution}.png")
        image_saved = False
        
        for part in response.parts:
            if image := part.as_image():
                image.save(output_path)
                image_saved = True
                break
        
        assert image_saved, f"Failed to save image for resolution {resolution}"
        assert os.path.exists(output_path), f"Image file not created for resolution {resolution}"
        assert os.path.getsize(output_path) > 0, f"Image file is empty for resolution {resolution}"

