"""Generate poster images using Gemini Image Generation (Nano Banana Pro or Nano Banana)."""
import os
from typing import Optional
from google import genai
from google.genai import types


def generate_poster(
    pdf_path: str,
    paper_info: dict,
    orientation: str = "landscape",
    resolution: str = "2K",
    model: str = "pro",
        language: str = "English",
        side_panel: Optional[str] = None,
        whatif_text: Optional[str] = None,
    existing_poster_path: Optional[str] = None,
    api_key: Optional[str] = None,
    output_path: str = "poster.png"
) -> str:
    """
    Generate a poster image from PDF file and paper information.
    
    Args:
        pdf_path: Path to the PDF file to upload and analyze
        paper_info: Dictionary with 'title', 'abstract', 'key_concepts', 'authors'
        orientation: 'landscape' or 'portrait'
        resolution: '1K', '2K', or '4K' (only used for 'pro' model)
        model: 'pro' (Nano Banana Pro) or 'flash' (Nano Banana)
        language: Language name for poster generation (e.g., 'English', 'Korean', 'Spanish')
        side_panel: Type of side panel to include (e.g., 'qa' for Q&A chat interface, None for no side panel)
        whatif_text: Optional "what if" idea text to incorporate into the poster
        existing_poster_path: Optional path to existing poster image to use as reference
        api_key: Google AI Studio API key (or use GEMINI_API_KEY/GOOGLE_API_KEY env var)
        output_path: Path to save the generated poster
    
    Returns:
        Path to the saved poster image
    """
    # Get API key
    if api_key is None:
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        raise ValueError(
            "API key not provided. Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable, "
            "or pass --api-key argument."
        )
    
    # Initialize client
    client = genai.Client(api_key=api_key)
    
    # Map model name to API model identifier
    model_map = {
        "pro": "gemini-3-pro-image-preview",  # Nano Banana Pro
        "flash": "gemini-2.5-flash-image"      # Nano Banana
    }
    
    if model not in model_map:
        raise ValueError(f"Invalid model: {model}. Must be 'pro' or 'flash'")
    
    api_model = model_map[model]
    
    # Determine aspect ratio based on orientation and side panel inclusion
    # If side_panel is set: Use wider aspect ratios for side-by-side layout (poster + side panel)
    # If no side_panel: Use standard poster aspect ratios
    # Note: API only supports: '1:1', '2:3', '3:2', '3:4', '4:3', '4:5', '5:4', '9:16', '16:9', '21:9'
    if side_panel:
        # Side-by-side layout: poster (left) + side panel (right)
        aspect_ratio = "21:9" if orientation == "landscape" else "4:3"
    else:
        # Standard poster layout (full width)
        aspect_ratio = "3:2" if orientation == "landscape" else "3:4"
    
    # Determine ordering principle based on orientation
    if orientation == "landscape":
        ordering_principle = """- Sections must follow column-first ordering principle: read top to bottom within each column, then move to the next column (left to right)
- Example to illustrate the principle (NOT a strict template):
  If using 3 columns with 2 rows: Column 1 (top→bottom), Column 2 (top→bottom), Column 3 (top→bottom)
  Reading flows vertically down each column before moving to the next column
- Adapt the layout to fit the content naturally while maintaining column-first ordering"""
    else:  # portrait
        ordering_principle = """- Sections must follow row-first ordering principle: read left to right within each row, then move to the next row (top to bottom)
- Example to illustrate the principle (NOT a strict template):
  If using 2 rows with 3 columns: Row 1 (left→right), Row 2 (left→right)
  Reading flows horizontally across each row before moving to the next row
- Adapt the layout to fit the content naturally while maintaining row-first ordering"""
    
    # Upload PDF file to Gemini
    try:
        uploaded_pdf = client.files.upload(
            file=pdf_path,
            config=types.UploadFileConfig(
                mimeType="application/pdf"
            )
        )
        pdf_uri = uploaded_pdf.uri
    except Exception as e:
        raise RuntimeError(f"Failed to upload PDF file: {e}") from e
    
    # Upload existing poster image if provided (for "what if" feature)
    uploaded_poster = None
    poster_uri = None
    if existing_poster_path:
        try:
            uploaded_poster = client.files.upload(
                file=existing_poster_path,
                config=types.UploadFileConfig(
                    mimeType="image/png"
                )
            )
            poster_uri = uploaded_poster.uri
        except Exception as e:
            raise RuntimeError(f"Failed to upload existing poster image: {e}") from e
    
    # Create poster prompt with orientation and layout specifications
    # Only include resolution in prompt for Pro model (Flash doesn't support it)
    resolution_text = f"- Resolution: {resolution}\n" if model == "pro" else ""
    
    # Add "what if" section if provided
    whatif_section = ""
    if whatif_text:
        whatif_section = f"""
WHAT IF IDEA TO INCORPORATE:
- The user wants to explore: "{whatif_text}"
- This is a new idea or variation to add on top of the existing research work
- Incorporate this "what if" concept into the poster while maintaining the core research content
- Show how this idea relates to or extends the existing work
- Make it visually clear that this is an extension or variation of the original research
- The poster should reflect both the original paper content AND this new "what if" idea
"""
    
    # Determine side panel content based on side_panel type
    if side_panel == "qa":
        # Side-by-side layout with Q&A
        layout_structure = """LAYOUT STRUCTURE:
The image must be divided into TWO DISTINCT SECTIONS side by side:

LEFT SIDE (60-65% of width): ACADEMIC POSTER"""
        side_panel_section = """
RIGHT SIDE (35-40% of width): Q&A CHAT INTERFACE
- Design a modern chat interface/messaging app style box
- Include a chat header/title area (e.g., "Questions & Answers" or "Q&A About This Paper")
- Display up to 4 common questions and answers about the paper in a chat bubble format (maximum 4 Q&A pairs total)
- Questions should appear as user messages (typically on the right, different color/style)
- Answers should appear as assistant/bot messages (typically on the left, different color/style)
- Use chat bubble design with rounded corners, appropriate colors, and clear visual distinction
- Questions should cover: methodology, key findings, applications, limitations, contributions
- Answers should be concise, informative, and directly address the questions
- Include scrollable chat appearance or multiple visible Q&A pairs
- Make it look like a real chat interface (modern, clean, professional)

VISUAL SEPARATION:
- Use a clear vertical divider or visual separator between the two sections
- Can use a subtle border, different background colors, or shadow effects
- Ensure both sections are visually distinct but harmoniously integrated"""
        layout_note = "Side-by-side design with Q&A chat interface"
        side_panel_description = "Q&A chat interface"
    elif side_panel:
        # Future: Other side panel types can be added here
        # For now, treat unknown types as no side panel
        layout_structure = """LAYOUT STRUCTURE:
The image is a single, full-width academic poster:"""
        side_panel_section = ""
        layout_note = "Full-width poster layout"
        side_panel_description = ""
    else:
        # Standard poster layout (full width)
        layout_structure = """LAYOUT STRUCTURE:
The image is a single, full-width academic poster:"""
        side_panel_section = ""
        layout_note = "Full-width poster layout"
        side_panel_description = ""
    
    # Determine if this is a "what if" variation
    is_whatif = whatif_text is not None and existing_poster_path is not None
    variation_note = " (variation incorporating a 'what if' idea)" if is_whatif else ""
    side_panel_note = f" with {side_panel_description}" if side_panel_description else ""
    
    poster_prompt = f"""
Create an academic poster{side_panel_note}{variation_note} for this research paper.
{whatif_section}
{layout_structure}
- Traditional academic poster layout with all key research information
- Use a clear grid-based layout with well-defined sections
- The number of sections, rows, and columns should be determined by the content and what makes sense for the paper
{ordering_principle}
- Ensure proper spacing between elements
- Organize content in logical flow
- Use visual separators to distinguish sections
- Maintain consistent margins and padding
- Ensure text blocks are properly aligned
{side_panel_section}

POSTER SPECIFICATIONS:
- Orientation: {orientation.upper()} ({aspect_ratio} aspect ratio)
{resolution_text}- Language: Generate all content (poster text{" and side panel content" if side_panel else ""}, labels) in {language}
- Overall Layout: {layout_note}

LEFT SIDE - POSTER DESIGN APPROACH:
- Visually appealing with title prominently displayed
- Clean, professional design with good typography and visual hierarchy
- Suitable for academic presentation and readable from a distance
- Focus on insights and key information, not lengthy descriptions

POSTER CONTENT STRATEGY:
- **Title**: Large, bold, prominent
- **Key Insights**: Focus on main contributions and findings (not detailed descriptions)
- **Visual Elements**: Include important figures, diagrams, and visual elements from the paper
- **Methodology**: Highlight the approach, not exhaustive details
- **Results**: Emphasize key results and conclusions with visual emphasis
- **Takeaways**: Make insights clear and immediately understandable
{f"""
Q&A CONTENT REQUIREMENTS (Right Side):
- Generate realistic, common questions that researchers or readers would ask about this paper
- Questions should be specific to the paper's content, methodology, and findings
- Answers should be accurate, concise, and directly based on the paper's content
- Cover diverse aspects: technical details, practical applications, limitations, future work
- Make Q&As informative and valuable for understanding the paper
""" if side_panel == "qa" else ""}
IMPORTANT: 
- The poster should prioritize visual communication over text. Use insights, highlights, and key points rather than descriptive paragraphs.
{f"- The Q&A side should look like a real, modern chat interface with proper chat bubble styling." if side_panel == "qa" else ""}
{f"- Both sides should work together as a cohesive single image that provides both visual poster information and interactive Q&A content." if side_panel == "qa" else "- The poster should convey the essence of the research quickly and effectively."}
"""
    
    # Create content with PDF file, existing poster (if provided), and text prompt
    contents = [
        types.Part(fileData=types.FileData(
            fileUri=pdf_uri,
            mimeType="application/pdf"
        ))
    ]
    
    # Add existing poster image if provided (for "what if" feature)
    if poster_uri:
        contents.append(
            types.Part(fileData=types.FileData(
                fileUri=poster_uri,
                mimeType="image/png"
            ))
        )
        # Add instruction to reference the existing poster
        contents.append(
            types.Part(text="\nREFERENCE: The uploaded image above is the existing poster. Use it as a reference and incorporate the 'what if' idea while maintaining the overall structure and style.\n")
        )
    
    contents.append(types.Part(text=poster_prompt))
    
    # Generate the poster image
    # Build ImageConfig - only include imageSize for Pro model (Flash doesn't support it)
    image_config_params = {"aspectRatio": aspect_ratio}
    if model == "pro":
        image_config_params["imageSize"] = resolution
    
    try:
        response = client.models.generate_content(
            model=api_model,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE'],
                image_config=types.ImageConfig(**image_config_params),
            )
        )
    except Exception as e:
        error_msg = str(e)
        if "API key" in error_msg or "API_KEY" in error_msg or "expired" in error_msg.lower():
            raise ValueError(
                f"API key error: {error_msg}\n"
                "Please check that your GEMINI_API_KEY or GOOGLE_API_KEY is valid and not expired."
            ) from e
        raise
    finally:
        # Clean up uploaded files
        try:
            client.files.delete(name=uploaded_pdf.name)
        except:
            pass  # Ignore cleanup errors
        if uploaded_poster:
            try:
                client.files.delete(name=uploaded_poster.name)
            except:
                pass  # Ignore cleanup errors
    
    # Extract and save image
    image_saved = False
    for part in response.parts:
        if image := part.as_image():
            image.save(output_path)
            image_saved = True
            break
    
    if not image_saved:
        raise RuntimeError("No image was generated in the API response")
    
    return output_path

