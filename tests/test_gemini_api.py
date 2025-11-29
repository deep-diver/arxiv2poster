"""
Test Gemini API call functionality according to PRD specifications.
"""
import os
import pytest
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


def test_gemini_api_client_initialization(api_key):
    """Test that Gemini API client can be initialized with API key."""
    client = genai.Client(api_key=api_key)
    assert client is not None


def test_gemini_api_call_works(gemini_client):
    """
    Test that Gemini API call works with usage from PRD.
    
    According to PRD:
    - Model: "gemini-3-pro-image-preview"
    - Response modalities: ['TEXT', 'IMAGE']
    - Image config with aspect_ratio and image_size
    """
    # Test prompt
    test_prompt = "Create a simple test image: a blue circle on white background"
    aspect_ratio = "16:9"
    resolution = "1K"  # Use 1K for faster testing
    
    # Generate content according to PRD specification
    # Note: ImageConfig uses camelCase for initialization, snake_case for access
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
    
    # Verify response is not None
    assert response is not None
    
    # Verify response has parts
    assert hasattr(response, 'parts')
    assert len(response.parts) > 0


def test_gemini_api_landscape_orientation(gemini_client):
    """Test Gemini API call with landscape orientation (16:9 aspect ratio)."""
    test_prompt = "A simple test image"
    aspect_ratio = "16:9"  # Landscape from PRD
    resolution = "1K"
    
    response = gemini_client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=test_prompt,
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE'],
            image_config=types.ImageConfig(
                aspectRatio=aspect_ratio,
                imageSize=resolution
            ),
        )
    )
    
    assert response is not None
    assert hasattr(response, 'parts')


def test_gemini_api_portrait_orientation(gemini_client):
    """Test Gemini API call with portrait orientation (9:16 aspect ratio)."""
    test_prompt = "A simple test image"
    aspect_ratio = "9:16"  # Portrait from PRD
    resolution = "1K"
    
    response = gemini_client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=test_prompt,
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE'],
            image_config=types.ImageConfig(
                aspectRatio=aspect_ratio,
                imageSize=resolution
            ),
        )
    )
    
    assert response is not None
    assert hasattr(response, 'parts')


def test_gemini_api_resolution_options(gemini_client):
    """Test Gemini API call with different resolution options from PRD."""
    test_prompt = "A simple test image"
    aspect_ratio = "16:9"
    
    # Test all resolution options from PRD: 1K, 2K, 4K
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
        
        assert response is not None
        assert hasattr(response, 'parts')

