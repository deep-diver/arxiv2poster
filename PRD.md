# Project Requirements Document (PRD)

## Project Overview

**arxiv2poster** is a command-line tool that automatically generates poster images from arXiv research papers. Given an arXiv paper ID, the tool downloads the paper PDF, processes it, and uses Google's **Nano Banana Pro** (Gemini 3.0 Image Generation) or **Nano Banana** (Gemini 2.5 Flash Image) model to create a visually appealing side-by-side layout: academic poster on the left and Q&A chat interface on the right, in either landscape or portrait orientation.

## Project Goals

- Automate the creation of academic poster images from arXiv papers with integrated Q&A chat interface
- Generate side-by-side layouts: academic poster (left) + Q&A chat interface (right)
- Support both landscape and portrait orientations with wider aspect ratios
- Provide a simple, CLI-first interface for researchers and academics
- Generate high-quality poster images suitable for presentations and sharing

## Workflow

The project follows this workflow:

1. **Input**: User provides an arXiv paper ID via CLI arguments
2. **Download**: System downloads the arXiv paper PDF using the provided ID
3. **Process**: Extract relevant information from the PDF (title, abstract, key concepts, etc.)
4. **Generate**: Use Nano Banana Pro to generate a poster image based on the paper content
5. **Output**: Save the generated poster image (landscape or portrait) to disk

## User Interface

### CLI-First Design

The project will be primarily a command-line interface (CLI) tool with the following argument structure:

```bash
arxiv2poster <arxiv_id> [options]
```

**Required Arguments:**
- `arxiv_ids`: One or more arXiv paper ID(s) (e.g., `2301.12345` or `cs.CV/2301.12345`)
  - Can specify multiple IDs to process in batch
  - Each paper will generate a separate poster file

**Optional Arguments:**
- `--model` / `-m`: Model to use (`pro` or `flash`, default: `pro`)
  - `pro`: Nano Banana Pro (Gemini 3.0 Image Generation) - supports resolution parameter, higher quality
  - `flash`: Nano Banana (Gemini 2.5 Flash Image) - lighter/cheaper, does not support resolution parameter
- `--orientation` / `-o`: Poster orientation (`landscape` or `portrait`, default: `landscape`)
  - When `--side-panel` is enabled: `landscape` uses `21:9`, `portrait` uses `4:3` (wider for side-by-side layout)
  - When no side panel (default): `landscape` uses `3:2`, `portrait` uses `3:4` (standard poster ratios)
- `--output-dir` / `-d`: Output directory for poster files (default: `outputs`)
- `--output` / `-out`: Output file path relative to output directory (default: `poster_<arxiv_id>_<orientation>_<language>.png`)
  - **Note**: Cannot be used when processing multiple arXiv IDs (each paper gets its own default filename)
  - Language in filename is normalized (lowercase, spaces replaced with underscores)
- `--resolution` / `-r`: Image resolution (`1K`, `2K`, or `4K`, default: `2K`)
  - **Note**: Only used with `--model pro` (Flash model does not support resolution parameter)
- `--language` / `-l`: Language for poster generation (full name, e.g., `English`, `Korean`, `Spanish`, `Japanese`, default: `English`)
  - All content (poster text, Q&As, labels) will be generated in the specified language
- `--side-panel`: Type of side panel to include (e.g., `qa` for Q&A chat interface)
  - By default, no side panel is included (standard poster only)
  - When no side panel: uses standard poster aspect ratios (3:2 for landscape, 3:4 for portrait)
  - When side panel is enabled: uses wider aspect ratios (21:9 for landscape, 4:3 for portrait)
  - Available options:
    - `qa`: Q&A chat interface with common questions and answers about the paper
    - `history`: Research history visualization showing the evolution of the field leading up to this paper (uses Google Search tool)
  - Future side panel types can be added (e.g., summary, keypoints, methodology)
- `--whatif`: "What if" idea text to incorporate into an existing poster
  - Requires an existing poster file matching current arguments (arxivID, orientation, language, side panel type)
  - Takes both the PDF and existing poster image to generate a variation
  - Output filename: `poster_<arxiv_id>_<orientation>_<language>_<side_panel|nopanel>_var_<number>.png`
  - Variant number is auto-incremented (var_1, var_2, etc.) if variants already exist
  - Cannot be used with multiple arXiv IDs
- `--api-key`: Google AI Studio API key (or use environment variable)

**Example Usage:**
```bash
# Basic usage (defaults to landscape 3:2, English, no Q&A, saves to outputs/poster_2301.12345_landscape_english_noqa.png)
arxiv2poster 2301.12345

# Process multiple papers in batch
arxiv2poster 1706.03762 2301.12345 cs.CV/2401.12345

# Portrait orientation (saves to outputs/poster_2301.12345_portrait_english_noqa.png)
arxiv2poster 2301.12345 --orientation portrait

# Custom output directory
arxiv2poster 2301.12345 --output-dir my_posters

# Custom output filename (relative to output directory, only works with single paper)
arxiv2poster 2301.12345 --orientation portrait --output my_poster.png

# High-resolution landscape poster (uses 3:2 aspect ratio) with Pro model
arxiv2poster cs.CV/2301.12345 --resolution 4K --orientation landscape --model pro

# Use lighter/cheaper Flash model (no resolution option)
arxiv2poster 2301.12345 --model flash --orientation portrait

# Generate poster in Korean
arxiv2poster 2301.12345 --language Korean

# Generate poster in Spanish
arxiv2poster 2301.12345 --language Spanish --orientation portrait

# Generate poster with Q&A chat interface (side-by-side layout)
arxiv2poster 2301.12345 --side-panel qa

# Generate poster with Q&A in Korean
arxiv2poster 2301.12345 --side-panel qa --language Korean

# Generate poster with research history visualization
arxiv2poster 2301.12345 --side-panel history

# "What if" feature: add idea to existing poster
arxiv2poster 2301.12345 --whatif "What if we apply this to medical imaging?"
# → outputs/poster_2301.12345_landscape_english_noqa_var_1.png

# Generate another variant with different idea
arxiv2poster 2301.12345 --whatif "What if we scale this to 1000x larger datasets?"
# → outputs/poster_2301.12345_landscape_english_noqa_var_2.png
```

## Technology Stack

### Core Components

1. **arXiv PDF Downloader**
   - Download PDF files from arXiv using paper IDs
   - Handle different arXiv ID formats (with/without category prefix)
   - Validate and verify successful downloads

2. **PDF Processing**
   - Extract text content from PDF files
   - Parse paper metadata (title, abstract, authors, etc.)
   - Identify key concepts and sections for poster generation

3. **Image Generation (Nano Banana Pro or Nano Banana)**
   - **Model Options**:
     - **Nano Banana Pro**: Gemini 3.0 Image Generation (`gemini-3-pro-image-preview`)
       - Higher quality output
       - Supports resolution parameter (1K, 2K, 4K)
     - **Nano Banana**: Gemini 2.5 Flash Image (`gemini-2.5-flash-image`)
       - Lighter/cheaper alternative
       - Does not support resolution parameter
   - **Provider**: Google AI Studio
   - Generate poster images based on paper content
   - Support landscape and portrait orientations
   - High-resolution output available with Pro model (1K, 2K, or 4K)

4. **CLI Interface**
   - Command-line argument parsing
   - User-friendly error messages and help text
   - Progress indicators and status updates

### Nano Banana Pro Key Features
- **High-Resolution Output**: Supports image generation up to 4K resolution
- **Advanced Editing Controls**: Precise adjustments for lighting, camera angles, depth of field, and color grading
- **Enhanced Text Rendering**: Improved accuracy in generating images with clear and accurate text
- **Subject Consistency**: Maintains consistency of up to five characters and fidelity of up to fourteen objects within a single workflow
- **Multiple Aspect Ratios**: Supports various aspect ratios (e.g., 1:1, 16:9, 9:16)
- **Resolution Options**: 1K, 2K, or 4K resolution outputs

## Functional Requirements

### arXiv Integration
- Support standard arXiv ID formats:
  - With category: `cs.CV/2301.12345`, `math.OC/2301.12345`
  - Without category: `2301.12345`
- Download PDF from arXiv using the official API or direct URL
- Handle download errors gracefully (invalid ID, network issues, etc.)
- Cache downloaded PDFs to avoid redundant downloads

### PDF Processing
- Upload entire PDF file to Gemini API for analysis
- Extract metadata (title, authors) for display purposes
- Pass the full PDF content to Gemini for comprehensive poster generation
- Gemini will analyze the entire paper including figures, tables, and all sections

### Poster Generation
- Upload entire PDF file to Gemini API for comprehensive analysis
- **Side-by-Side Layout Structure:**
  - **Left Side (approximately 70-75% width)**: Traditional academic poster with all key research information
    - Clear grid-based layout with well-defined sections
    - **Layout ordering depends on orientation:**
      - **Landscape**: Column-first ordering principle - read top to bottom within each column, then move to the next column (left to right)
      - **Portrait**: Row-first ordering principle - read left to right within each row, then move to the next row (top to bottom)
    - The number of sections, rows, and columns should be determined by the content and what makes sense for the paper
    - Adapt the layout to fit the content naturally while maintaining the appropriate ordering principle
    - Prioritize visual communication and insights over lengthy text descriptions
    - Highlight important information and key insights
    - Incorporate paper title, key concepts, and visual elements from the paper
  - **Right Side (approximately 25-30% width, NOT TOO WIDE)**: Q&A Chat Interface or Research History Visualization
    - The side panel should be narrow, similar to a 9:16 portrait aspect ratio in terms of width proportion
    - Keep the side panel compact and focused, not taking up too much horizontal space
    - For Q&A: Modern chat interface/messaging app style box
    - Chat header/title area (e.g., "Questions & Answers" or "Q&A About This Paper")
    - Display up to 4 common questions and answers about the paper in chat bubble format (maximum 4 Q&A pairs total)
    - Questions appear as user messages (typically right-aligned, different color/style)
    - Answers appear as assistant/bot messages (typically left-aligned, different color/style)
    - Chat bubble design with rounded corners, appropriate colors, and clear visual distinction
    - Questions cover: methodology, key findings, applications, limitations, contributions
    - Answers are concise, informative, and directly address the questions
    - Scrollable chat appearance or multiple visible Q&A pairs
    - Modern, clean, professional chat interface appearance
    - For History: Timeline or history visualization panel
    - Research history header/title area (e.g., "Research History" or "Evolution of This Field")
    - Visualize research history leading up to this paper using Google Search
    - Display key milestones, influential papers, and important developments chronologically
    - Timeline design with dates, events, visual connections, and important breakthroughs
    - Show how the current paper fits into the broader research landscape
    - Based on actual research developments found through web search
  - **Visual Separation**: Clear vertical divider or visual separator between the two sections
- Support both landscape (21:9) and portrait (4:3) orientations with wider aspect ratios for side-by-side layout
- Generate high-quality images suitable for printing or digital display
- Use supported aspect ratios only: '1:1', '2:3', '3:2', '3:4', '4:3', '4:5', '5:4', '9:16', '16:9', '21:9'

### Error Handling
- Validate arXiv IDs before processing
- Handle API rate limits and errors
- Provide clear error messages to users
- Support retry mechanisms for transient failures

## Integration Guide: Nano Banana Pro via Google AI Studio

### Step 1: Access Google AI Studio
1. Navigate to [Google AI Studio](https://ai.google.dev/gemini-api/docs/image-generation)
2. Sign in with your Google account

### Step 2: Set Up Project and API Access
1. Create a new project or select an existing one in Google Cloud Console
2. Enable billing to access the Nano Banana Pro API
3. Navigate to the API keys section in AI Studio
4. Generate a new API key
5. **Important**: Store this key securely (use environment variables, not hardcoded in source code)

### Step 3: Install Required Libraries

For Python projects, install the Google Generative AI library:

```bash
pip install google-genai
```

### Step 4: Implementation Example for Poster Generation with PDF Upload

```python
from google import genai
from google.genai import types

# Initialize the client with your API key
client = genai.Client(api_key='YOUR_API_KEY')

# Upload PDF file to Gemini
pdf_path = "paper.pdf"
uploaded_file = client.files.upload(
    file=pdf_path,
    config=types.UploadFileConfig(
        mimeType="application/pdf"
    )
)

# Create poster generation prompt
poster_prompt = f"""
Create a side-by-side academic poster with Q&A chat interface for this research paper.

LAYOUT STRUCTURE:
The image must be divided into TWO DISTINCT SECTIONS side by side:

LEFT SIDE (approximately 70-75% of width): ACADEMIC POSTER
- Traditional academic poster layout with all key research information
- Use a clear grid-based layout with well-defined sections
- **Ordering principle depends on orientation:**
  - **Landscape**: Column-first ordering - read top to bottom within each column, then move to the next column (left to right)
    Example: Column 1 (top→bottom), Column 2 (top→bottom), Column 3 (top→bottom)
  - **Portrait**: Row-first ordering - read left to right within each row, then move to the next row (top to bottom)
    Example: Row 1 (left→right), Row 2 (left→right), Row 3 (left→right)
- These examples are to illustrate the principle (NOT strict templates)
- Adapt the layout to fit the content naturally while maintaining the appropriate ordering principle
- Ensure proper spacing between elements
- Organize content in logical flow
- Use visual separators to distinguish sections
- Maintain consistent margins and padding
- Ensure text blocks are properly aligned

RIGHT SIDE (approximately 25-30% of width, NOT TOO WIDE): Q&A CHAT INTERFACE or RESEARCH HISTORY VISUALIZATION
- The side panel should be narrow, similar to a 9:16 portrait aspect ratio in terms of width proportion
- Keep the side panel compact and focused, not taking up too much horizontal space
- For Q&A: Design a modern chat interface/messaging app style box
  - Include a chat header/title area (e.g., "Questions & Answers" or "Q&A About This Paper")
  - Display up to 4 common questions and answers about the paper in a chat bubble format (maximum 4 Q&A pairs total)
  - Questions should appear as user messages (typically on the right, different color/style)
  - Answers should appear as assistant/bot messages (typically on the left, different color/style)
  - Use chat bubble design with rounded corners, appropriate colors, and clear visual distinction
  - Questions should cover: methodology, key findings, applications, limitations, contributions
  - Answers should be concise, informative, and directly address the questions
  - Include scrollable chat appearance or multiple visible Q&A pairs
  - Make it look like a real chat interface (modern, clean, professional)
- For History: Design a timeline or history visualization panel
  - Include a header/title area (e.g., "Research History" or "Evolution of This Field")
  - Visualize the research history leading up to this paper using information from Google Search
  - Display key milestones, influential papers, and important developments in chronological order
  - Use timeline design with vertical or horizontal layout, key dates, visual connections, and important breakthroughs
  - Show how this current paper builds upon or relates to previous work
  - Include visual elements like timeline markers, connecting lines, icons, and color coding
  - The history should be based on actual research developments found through web search

VISUAL SEPARATION:
- Use a clear vertical divider or visual separator between the two sections
- Can use a subtle border, different background colors, or shadow effects
- Ensure both sections are visually distinct but harmoniously integrated

POSTER SPECIFICATIONS:
- Orientation: {orientation.upper()} ({aspect_ratio} aspect ratio)
- Resolution: {resolution}
- Language: Generate all content (poster text, Q&As, labels) in {language}
- Overall Layout: Side-by-side design with clear visual separation

LEFT SIDE - POSTER DESIGN APPROACH:
- Visually appealing with title prominently displayed
- Clean, professional design with good typography and visual hierarchy
- Suitable for academic presentation and readable from a distance
- Focus on insights and key information, not lengthy descriptions

CONTENT STRATEGY - HIGHLIGHT IMPORTANT INFORMATION:
- **Title**: Large, bold, prominent
- **Key Insights**: Focus on main contributions and findings (not detailed descriptions)
- **Visual Elements**: Include important figures, diagrams, and visual elements from the paper
- **Methodology**: Highlight the approach, not exhaustive details
- **Results**: Emphasize key results and conclusions with visual emphasis
- **Takeaways**: Make insights clear and immediately understandable

IMPORTANT: Prioritize visual communication over text. Use insights, highlights, and key points rather than descriptive paragraphs. The poster should convey the essence of the research quickly and effectively.
"""

# Create content with PDF file and text prompt
orientation = "landscape"  # or "portrait"
aspect_ratio = "3:2" if orientation == "landscape" else "3:4"
resolution = "2K"

contents = [
    types.Part(fileData=types.FileData(
        fileUri=uploaded_file.uri,
        mimeType="application/pdf"
    )),
    types.Part(text=poster_prompt)
]

# Generate the poster image
# Add Google Search tool if history side panel is enabled
tools = None
if side_panel == "history":
    tools = [types.Tool(googleSearch=types.GoogleSearch())]

config_params = {
    "response_modalities": ['TEXT', 'IMAGE'],
    "image_config": types.ImageConfig(
        aspectRatio=aspect_ratio,
        imageSize=resolution
    ),
}
if tools:
    config_params["tools"] = tools

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=contents,
    config=types.GenerateContentConfig(**config_params)
)

# Save the generated poster
for part in response.parts:
    if image := part.as_image():
        image.save("poster.png")

# Clean up uploaded file
client.files.delete(name=uploaded_file.name)
```

### Step 5: API Response Handling
- The API returns both text and image parts in the response
- Process and save the image parts appropriately
- Handle errors and rate limits gracefully

### Step 6: Configuration Parameters

Key parameters for image generation:
- **model**: `"gemini-3-pro-image-preview"` (Nano Banana Pro model identifier)
- **contents**: Text prompt describing the desired image
- **aspect_ratio**: Determined by orientation setting (must be one of API-supported ratios)
  - `"3:2"` for landscape orientation (optimized for poster proportions, taller than 16:9)
  - `"3:4"` for portrait orientation (optimized for poster proportions, wider than 9:16)
  - **API Constraint**: Only these ratios are supported: '1:1', '2:3', '3:2', '3:4', '4:3', '4:5', '5:4', '9:16', '16:9', '21:9'
  - Custom aspect ratios are not supported by the API
- **image_size**: Resolution setting ("1K", "2K", or "4K")
- **response_modalities**: Set to `['TEXT', 'IMAGE']` to receive both text and image responses

## arXiv Integration

### Downloading Papers from arXiv

arXiv papers can be downloaded using the following methods:

1. **Direct URL Method**:
   - Format: `https://arxiv.org/pdf/{arxiv_id}.pdf`
   - Example: `https://arxiv.org/pdf/2301.12345.pdf`
   - Works for both formats: with or without category prefix

2. **arXiv API** (optional, for metadata):
   - Use arXiv API to fetch paper metadata before downloading
   - API endpoint: `http://export.arxiv.org/api/query?id_list={arxiv_id}`

3. **Python Libraries**:
   - `arxiv` package: `pip install arxiv`
   - Provides convenient methods to download papers and extract metadata

**Example Implementation:**
```python
import arxiv

# Search and download paper
paper = arxiv.Client().results(arxiv.Search(id_list=["2301.12345"]))
paper = next(paper)
paper.download_pdf(dirpath="./", filename="paper.pdf")
```

## Additional Resources

- **Google AI Studio Documentation**: [Gemini API Image Generation](https://ai.google.dev/gemini-api/docs/image-generation)
- **Nano Banana Pro Overview**: [Gemini Image Generation Overview](https://gemini.google/overview/image-generation/)
- **arXiv API Documentation**: [arXiv API User's Manual](https://arxiv.org/help/api/user-manual)
- **Python arxiv Package**: [arxiv-py on PyPI](https://pypi.org/project/arxiv/)

## Important Notes

### Security & Configuration
- Google AI Studio API keys must be kept secure and never committed to version control
- Use environment variables (e.g., `GOOGLE_AI_API_KEY`) for API key management
- Consider using `.env` files for local development (and add to `.gitignore`)

### Usage & Limits
- Ensure compliance with Google's usage policies and guidelines
- Review rate limits and pricing before production deployment
- arXiv papers are freely available, but respect their terms of use

### Development Considerations
- Test thoroughly with various arXiv paper IDs and formats
- Handle edge cases: papers without abstracts, very long papers, etc.
- Consider implementing caching for downloaded PDFs to reduce redundant downloads
- Add progress indicators for long-running operations (PDF download, image generation)
- **Important**: When requirements change or are added, update PRD.md accordingly to keep documentation in sync
- Aspect ratios are limited to API-supported values only
- Poster generation prioritizes visual communication and insights over text-heavy descriptions

