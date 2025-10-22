from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import textwrap
import markdown

ROOT = Path(__file__).parent
MD_FILE = ROOT / "paper.md"
OUT_PDF = ROOT / "paper.pdf"


def md_to_plain(md_text: str) -> str:
    # Convert markdown to simple plaintext by stripping markup
    # We'll first convert to HTML and then remove tags naively.
    html = markdown.markdown(md_text)
    # Remove HTML tags (simple approach)
    import re
    text = re.sub(r"<[^>]+>", "", html)
    # Unescape HTML entities
    import html as httplib_html
    text = httplib_html.unescape(text)
    return text


def render_pdf(text: str, out_path: Path):
    c = canvas.Canvas(str(out_path), pagesize=letter)
    width, height = letter
    margin = 72  # 1 inch
    max_width = width - 2 * margin
    y = height - margin
    line_height = 12

    wrapper = textwrap.TextWrapper(width=95)
    for paragraph in text.split('\n\n'):
        if not paragraph.strip():
            y -= line_height
            continue
        lines = wrapper.wrap(paragraph)
        for line in lines:
            if y < margin + line_height:
                c.showPage()
                y = height - margin
            c.drawString(margin, y, line)
            y -= line_height
        y -= line_height / 2

    c.save()


def main():
    if not MD_FILE.exists():
        print(f"Missing {MD_FILE}")
        return 2
    md = MD_FILE.read_text(encoding='utf-8')
    plain = md_to_plain(md)
    render_pdf(plain, OUT_PDF)
    print(f"Wrote fallback PDF to {OUT_PDF}")


if __name__ == '__main__':
    raise SystemExit(main())
