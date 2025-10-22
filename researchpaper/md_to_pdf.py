import os
from pathlib import Path
import markdown
import cairosvg
from weasyprint import HTML


ROOT = Path(__file__).parent
MD_FILE = ROOT / "paper.md"
OUT_PDF = ROOT / "paper.pdf"


def svg_to_png(svg_path: Path) -> Path:
    png_path = svg_path.with_suffix('.png')
    try:
        cairosvg.svg2png(url=str(svg_path), write_to=str(png_path))
        return png_path
    except Exception as e:
        print(f"Failed to convert {svg_path} -> PNG: {e}")
        raise


def convert_markdown_to_html(md_text: str) -> str:
    # Use python-markdown with extensions for code highlighting
    return markdown.markdown(md_text, extensions=["fenced_code", "codehilite"])


def main():
    if not MD_FILE.exists():
        print(f"Missing {MD_FILE}")
        return 2

    md = MD_FILE.read_text(encoding='utf-8')

    # Find SVG references and convert them to PNG
    # This is a simple heuristic: look for '![alt](path.svg)'
    import re
    svg_paths = set(re.findall(r"!\[[^\]]*\]\(([^)]+\.svg)\)", md))
    for rel in svg_paths:
        svg_path = (ROOT / rel).resolve()
        if svg_path.exists():
            print(f"Converting {svg_path.name} -> PNG")
            png_path = svg_to_png(svg_path)
            md = md.replace(f"({rel})", f"({png_path.name})")
        else:
            print(f"Warning: referenced SVG not found: {rel}")

    html = convert_markdown_to_html(md)

    # Wrap in minimal HTML
    full_html = f"""
    <html>
      <head>
        <meta charset="utf-8">
        <style>
          body {{ font-family: Arial, Helvetica, sans-serif; margin: 1in; }}
          pre {{ background: #f4f4f4; padding: 8px; overflow-x: auto; }}
          code {{ font-family: monospace; }}
        </style>
      </head>
      <body>
        {html}
      </body>
    </html>
    """

    # Write intermediary HTML for debugging
    html_path = ROOT / "paper_intermediate.html"
    html_path.write_text(full_html, encoding='utf-8')

    print(f"Rendering PDF to {OUT_PDF}")
    HTML(string=full_html, base_url=str(ROOT)).write_pdf(str(OUT_PDF))
    print("Done")


if __name__ == '__main__':
    raise SystemExit(main())
