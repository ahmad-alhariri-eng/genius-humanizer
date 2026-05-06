"""
CLI entry point for genius-humanizer.
Called by the Node.js wrapper.
Usage: python cli_humanize.py <input_file>
Output: humanized text to stdout
Progress: sent to stderr
"""
import sys
import os

# Add parent directory to path so we can import genius_humanizer
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from genius_humanizer import GeniusHumanizer


def main():
    if len(sys.argv) < 2:
        print("Usage: python cli_humanize.py <input_file>", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}", file=sys.stderr)
        sys.exit(1)

    # Read input
    try:
        if input_file.endswith('.docx'):
            try:
                import docx
                doc = docx.Document(input_file)
                text = "\n".join([p.text for p in doc.paragraphs])
            except ImportError:
                print("Error: python-docx required for .docx files. Run: pip install python-docx", file=sys.stderr)
                sys.exit(1)
        else:
            with open(input_file, 'r', encoding='utf-8') as f:
                text = f.read()
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    if not text.strip():
        print("Error: File is empty.", file=sys.stderr)
        sys.exit(1)

    # Progress callback
    def progress(pct):
        print(f"Progress: {pct}%", file=sys.stderr, flush=True)

    # Initialize and run
    try:
        humanizer = GeniusHumanizer()
        result = humanizer.humanize(text, progress_callback=progress)
        # Output result to stdout
        print(result)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
