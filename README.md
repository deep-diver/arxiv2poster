# arxiv2poster

A command-line tool that automatically generates poster images from arXiv research papers using Google's Gemini Image Generation models (Nano Banana Pro or Nano Banana).

## Installation

### From Source

```bash
# Clone the repository
git clone <repository-url>
cd arxiv2poster

# Install in development mode
pip install -e .
```

### Dependencies

The package requires:
- Python 3.8+
- `google-genai>=0.2.0`
- `arxiv>=2.1.0`

## Setup

1. Get a Google AI Studio API key from [Google AI Studio](https://ai.google.dev/gemini-api/docs/image-generation)
2. Set the API key as an environment variable:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   # or
   export GOOGLE_API_KEY="your-api-key-here"
   ```

## Usage

### Basic Usage

```bash
# Generate a poster from an arXiv paper (default: landscape, 2K resolution, English, no Q&A)
# Saves to outputs/poster_1706.03762_landscape_english_noqa.png
arxiv2poster 1706.03762
```

### Batch Processing

```bash
# Process multiple papers in batch
# Each paper will be saved with its default filename in the output directory
arxiv2poster 1706.03762 2301.12345 cs.CV/2401.12345

# Batch processing with custom options (applied to all papers)
arxiv2poster 1706.03762 2301.12345 --orientation portrait --resolution 4K --model pro
```

### Advanced Usage

```bash
# Portrait orientation (saves to outputs/poster_1706.03762_portrait.png)
arxiv2poster 1706.03762 --orientation portrait

# Custom output directory
arxiv2poster 1706.03762 --output-dir my_posters

# Custom output filename (relative to output directory, only works with single paper)
arxiv2poster 1706.03762 --orientation portrait --output my_poster.png

# High-resolution landscape poster with Pro model
arxiv2poster cs.CV/2301.12345 --resolution 4K --orientation landscape --model pro

# Use lighter/cheaper Flash model (no resolution option)
arxiv2poster 1706.03762 --model flash --orientation portrait

# Generate poster in Korean
arxiv2poster 1706.03762 --language Korean

# Generate poster in Spanish
arxiv2poster 1706.03762 --language Spanish --orientation portrait

# Generate poster with Q&A chat interface (side-by-side layout)
arxiv2poster 1706.03762 --side-panel qa

# Generate poster with Q&A in Korean
arxiv2poster 1706.03762 --side-panel qa --language Korean

# "What if" feature: add idea to existing poster
arxiv2poster 1706.03762 --whatif "What if we apply this to medical imaging?"
# → outputs/poster_1706.03762_landscape_english_noqa_var_1.png

# Generate another variant with different idea
arxiv2poster 1706.03762 --whatif "What if we scale this to 1000x larger datasets?"
# → outputs/poster_1706.03762_landscape_english_noqa_var_2.png

# With verbose output
arxiv2poster 1706.03762 --verbose

# Using API key as argument (instead of environment variable)
arxiv2poster 1706.03762 --api-key YOUR_API_KEY
```

### Command Options

- `arxiv_ids` (required): One or more arXiv paper ID(s) (e.g., `1706.03762` or `cs.CV/2301.12345`)
  - Can specify multiple IDs to process in batch
  - Each paper will generate a separate poster file
- `--model`, `-m`: Model to use (`pro` or `flash`, default: `pro`)
  - `pro`: Nano Banana Pro (Gemini 3.0 Image Generation) - supports resolution parameter, higher quality
  - `flash`: Nano Banana (Gemini 2.5 Flash Image) - lighter/cheaper, does not support resolution parameter
- `--orientation`, `-o`: Poster orientation (`landscape` or `portrait`, default: `landscape`)
  - When `--side-panel` is enabled: `landscape` uses `21:9`, `portrait` uses `4:3` (wider for side-by-side layout)
  - When no side panel (default): `landscape` uses `3:2`, `portrait` uses `3:4` (standard poster ratios)
- `--output-dir`, `-d`: Output directory for poster files (default: `outputs`)
- `--output`, `-out`: Output file path relative to output directory (default: `poster_<arxiv_id>_<orientation>_<language>.png`)
  - **Note**: Cannot be used when processing multiple arXiv IDs (each paper gets its own default filename)
  - Language in filename is normalized (lowercase, spaces replaced with underscores)
- `--resolution`, `-r`: Image resolution (`1K`, `2K`, or `4K`, default: `2K`)
  - **Note**: Only used with `--model pro` (Flash model does not support resolution parameter)
- `--language`, `-l`: Language for poster generation (full name, e.g., `English`, `Korean`, `Spanish`, `Japanese`, default: `English`)
  - All content (poster text, Q&As, labels) will be generated in the specified language
- `--side-panel`: Type of side panel to include (e.g., `qa` for Q&A chat interface)
  - By default, no side panel is included (standard poster only)
  - When no side panel: uses standard poster aspect ratios (3:2 for landscape, 3:4 for portrait)
  - When side panel is enabled: uses wider aspect ratios (21:9 for landscape, 4:3 for portrait)
  - Available options:
    - `qa`: Q&A chat interface with common questions and answers about the paper
  - Future side panel types can be added (e.g., summary, keypoints, methodology)
- `--whatif`: "What if" idea text to incorporate into an existing poster
  - Requires an existing poster file matching current arguments (arxivID, orientation, language, side panel type)
  - Takes both the PDF and existing poster image to generate a variation
  - Output filename: `poster_<arxiv_id>_<orientation>_<language>_<side_panel|nopanel>_var_<number>.png`
  - Variant number is auto-incremented (var_1, var_2, etc.) if variants already exist
  - Cannot be used with multiple arXiv IDs
- `--api-key`: Google AI Studio API key (or use `GEMINI_API_KEY`/`GOOGLE_API_KEY` env var)
- `--verbose`, `-v`: Enable verbose output

## Running Tests

To run all tests:
```bash
pytest tests/
```

To run specific test files:
```bash
# Test Gemini API calls
pytest tests/test_gemini_api.py

# Test image generation and saving
pytest tests/test_image_generation.py

# Test arXiv PDF download
pytest tests/test_arxiv_download.py
```

To run tests with verbose output:
```bash
pytest tests/ -v
```

## Test Requirements

- `GEMINI_API_KEY` or `GOOGLE_API_KEY` environment variable must be set for Gemini API tests
  - Note: Tests will be skipped if the API key is not set
  - If the API key is expired or invalid, tests will fail with authentication errors
- Internet connection required for arXiv download tests

## Project Status

This project is in development. See `PRD.md` for detailed project requirements.

