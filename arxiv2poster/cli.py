"""Command-line interface for arxiv2poster."""
import argparse
import os
import re
import sys
from pathlib import Path
from .arxiv_downloader import download_arxiv_pdf
from .pdf_processor import extract_paper_info
from .poster_generator import generate_poster


def normalize_arxiv_id(arxiv_id: str) -> str:
    """Normalize arXiv ID format."""
    # Remove any whitespace
    arxiv_id = arxiv_id.strip()
    # If it starts with 'arxiv:', remove it
    if arxiv_id.startswith('arxiv:'):
        arxiv_id = arxiv_id[6:]
    return arxiv_id


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate poster images from arXiv research papers using Gemini Image Generation (Nano Banana Pro or Nano Banana)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (defaults to landscape 3:2, English, no Q&A, saves to outputs/poster_1706.03762_landscape_english_noqa.png)
  arxiv2poster 1706.03762

  # Process multiple papers in batch
  arxiv2poster 1706.03762 2301.12345 cs.CV/2401.12345

  # Portrait orientation (saves to outputs/poster_1706.03762_portrait_english.png)
  arxiv2poster 1706.03762 --orientation portrait

  # Custom output directory
  arxiv2poster 1706.03762 --output-dir my_posters

  # Custom output filename (only works with single paper)
  arxiv2poster 1706.03762 --orientation portrait --output my_poster.png

  # High-resolution landscape poster (3:2 aspect ratio) with Pro model
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
        """
    )
    
    # Required argument(s) - can accept multiple IDs
    parser.add_argument(
        'arxiv_ids',
        type=str,
        nargs='+',
        help='arXiv paper ID(s) (e.g., 1706.03762 or cs.CV/2301.12345). Can specify multiple IDs to process in batch'
    )
    
    # Optional arguments
    parser.add_argument(
        '--orientation', '-o',
        type=str,
        choices=['landscape', 'portrait'],
        default='landscape',
        help='Poster orientation: landscape or portrait. Default: landscape (aspect ratio depends on --with-qa)'
    )
    
    parser.add_argument(
        '--output-dir', '-d',
        type=str,
        default='outputs',
        help='Output directory for poster files. Default: outputs'
    )
    
    parser.add_argument(
        '--output', '-out',
        type=str,
        default=None,
        help='Output file path (relative to output directory). Default: poster_<arxiv_id>_<orientation>_<language>_<qa|noqa>.png'
    )
    
    parser.add_argument(
        '--model', '-m',
        type=str,
        choices=['pro', 'flash'],
        default='pro',
        help='Model to use: pro (Nano Banana Pro, supports resolution) or flash (Nano Banana, lighter/cheaper, no resolution). Default: pro'
    )
    
    parser.add_argument(
        '--resolution', '-r',
        type=str,
        choices=['1K', '2K', '4K'],
        default='2K',
        help='Image resolution: 1K, 2K, or 4K. Default: 2K (only used with --model pro)'
    )
    
    parser.add_argument(
        '--language', '-l',
        type=str,
        default='English',
        help='Language for poster generation (full name, e.g., "English", "Korean", "Spanish", "Japanese"). Default: English'
    )
    
    parser.add_argument(
        '--side-panel',
        type=str,
        choices=['qa'],
        default=None,
        help='Type of side panel to include: "qa" for Q&A chat interface (side-by-side layout). By default, no side panel is included.'
    )
    
    parser.add_argument(
        '--whatif',
        type=str,
        default=None,
        help='"What if" idea text to incorporate into an existing poster. Requires an existing poster file matching current arguments.'
    )
    
    parser.add_argument(
        '--api-key',
        type=str,
        default=None,
        help='Google AI Studio API key (or use GEMINI_API_KEY/GOOGLE_API_KEY env var)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Normalize arXiv IDs
    arxiv_ids = [normalize_arxiv_id(arxiv_id) for arxiv_id in args.arxiv_ids]
    
    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Validate output argument when multiple IDs are provided
    if len(arxiv_ids) > 1 and args.output is not None:
        print("❌ Error: --output option cannot be used when processing multiple arXiv IDs.", file=sys.stderr)
        print("   Each paper will be saved with its default filename in the output directory.", file=sys.stderr)
        return 1
    
    # Validate resolution is only used with Pro model
    if args.model == "flash" and args.resolution != "2K":
        print("⚠️  Warning: --resolution is ignored when using --model flash (Nano Banana doesn't support resolution).", file=sys.stderr)
    
    # Validate whatif argument
    if args.whatif and len(arxiv_ids) > 1:
        print("❌ Error: --whatif cannot be used when processing multiple arXiv IDs.", file=sys.stderr)
        return 1
    
    # Process each arXiv ID
    success_count = 0
    failed_ids = []
    
    for idx, arxiv_id in enumerate(arxiv_ids, 1):
        if len(arxiv_ids) > 1:
            print(f"\n[{idx}/{len(arxiv_ids)}] Processing {arxiv_id}...")
        
        try:
            # Extract clean ID for filename (used in multiple places)
            clean_id = arxiv_id.split('/')[-1] if '/' in arxiv_id else arxiv_id
            
            # Normalize language name for filename (lowercase, replace spaces with underscores)
            lang_normalized = args.language.lower().replace(' ', '_')
            side_panel_suffix = args.side_panel if args.side_panel else "nopanel"
            
            # Determine output path for this paper
            if args.output is None:
                
                # Handle "what if" feature
                if args.whatif:
                    # Find existing poster file
                    base_filename = f"poster_{clean_id}_{args.orientation}_{lang_normalized}_{side_panel_suffix}.png"
                    existing_poster_path = output_dir / base_filename
                    
                    if not existing_poster_path.exists():
                        print(f"❌ Error: Existing poster file not found: {existing_poster_path}", file=sys.stderr)
                        print(f"   Please generate the base poster first without --whatif.", file=sys.stderr)
                        failed_ids.append(arxiv_id)
                        continue
                    
                    # Find next variant number
                    variant_num = 1
                    while True:
                        variant_filename = f"poster_{clean_id}_{args.orientation}_{lang_normalized}_{side_panel_suffix}_var_{variant_num}.png"
                        variant_path = output_dir / variant_filename
                        if not variant_path.exists():
                            break
                        variant_num += 1
                    
                    filename = variant_filename
                    output_path = str(output_dir / filename)
                else:
                    filename = f"poster_{clean_id}_{args.orientation}_{lang_normalized}_{side_panel_suffix}.png"
                    output_path = str(output_dir / filename)
            else:
                # Single paper with custom output
                if not os.path.isabs(args.output):
                    output_path = str(output_dir / args.output)
                else:
                    output_path = args.output
                # Ensure parent directory exists
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            if args.verbose:
                print(f"📄 Downloading paper {arxiv_id} from arXiv...")
            
            # Step 1: Download PDF
            pdf_path, metadata = download_arxiv_pdf(arxiv_id)
            
            if args.verbose:
                print(f"✓ Downloaded: {metadata.get('title', 'Unknown')}")
                print(f"  Authors: {', '.join(metadata.get('authors', [])[:3])}")
            
            # Step 2: Extract paper information (for metadata display)
            if args.verbose:
                print("📝 Extracting paper metadata...")
            
            paper_info = extract_paper_info(pdf_path, metadata)
            
            if args.verbose:
                print(f"✓ Paper metadata extracted")
            
            # Step 3: Generate poster (pass entire PDF to Gemini)
            model_display = "Nano Banana Pro" if args.model == "pro" else "Nano Banana"
            resolution_display = f", {args.resolution}" if args.model == "pro" else ""
            whatif_display = f" with 'what if' idea: '{args.whatif}'" if args.whatif else ""
            if args.verbose:
                print(f"📤 Uploading PDF{' and existing poster' if args.whatif else ''} to Gemini and generating poster ({args.orientation}{resolution_display}, {model_display}){whatif_display}...")
                print(f"   This may take a minute...")
            
            # Get existing poster path for "what if" feature
            existing_poster_path = None
            if args.whatif:
                base_filename = f"poster_{clean_id}_{args.orientation}_{lang_normalized}_{side_panel_suffix}.png"
                existing_poster_path = str(output_dir / base_filename)
            
            final_output_path = generate_poster(
                pdf_path=pdf_path,
                paper_info=paper_info,
                orientation=args.orientation,
                resolution=args.resolution,
                model=args.model,
                language=args.language,
                side_panel=args.side_panel,
                whatif_text=args.whatif,
                existing_poster_path=existing_poster_path,
                api_key=args.api_key,
                output_path=output_path
            )
            
            if args.verbose:
                print(f"✓ Poster generated successfully!")
            
            print(f"✨ Poster saved to: {final_output_path}")
            success_count += 1
            
            # Clean up temporary PDF if it was in a temp directory
            if '/tmp' in pdf_path:
                try:
                    os.remove(pdf_path)
                except:
                    pass  # Ignore cleanup errors
            
        except ValueError as e:
            print(f"❌ Error processing {arxiv_id}: {e}", file=sys.stderr)
            failed_ids.append(arxiv_id)
        except Exception as e:
            print(f"❌ Unexpected error processing {arxiv_id}: {e}", file=sys.stderr)
            if args.verbose:
                import traceback
                traceback.print_exc()
            failed_ids.append(arxiv_id)
    
    # Summary for multiple IDs
    if len(arxiv_ids) > 1:
        print(f"\n{'='*60}")
        print(f"Summary: {success_count}/{len(arxiv_ids)} posters generated successfully")
        if failed_ids:
            print(f"Failed IDs: {', '.join(failed_ids)}")
        print(f"{'='*60}")
        return 0 if success_count == len(arxiv_ids) else 1
    
    return 0 if success_count > 0 else 1
        


if __name__ == '__main__':
    sys.exit(main())

