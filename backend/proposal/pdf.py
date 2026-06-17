import re
from fpdf import FPDF
from pathlib import Path
from datetime import date

SECTION_HEADERS = {
    "EXECUTIVE SUMMARY", "THE CHALLENGE", "OUR PROPOSED SOLUTION",
    "WHAT YOU GET", "INVESTMENT", "TIMELINE", "NEXT STEPS", "CLOSING"
}

TIMELINE_PREFIXES = ("Week ", "Phase ", "Day ")


class ProposalPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "SouthPeak Systems LLC  |  Confidential Proposal", align="R")
        self.ln(4)
        self.set_draw_color(220, 220, 220)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"SouthPeak Systems LLC  |  southpeak-systems.com  |  Page {self.page_no()}", align="C")


def _clean_line(text: str) -> str:
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # markdown links
    text = re.sub(r'https?://\S+', '', text)               # bare URLs
    text = re.sub(r'^-{3,}$', '', text.strip())            # --- dividers
    text = re.sub(r'^#{1,6}\s*', '', text)                 # ## markdown headers
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)          # **bold**
    text = re.sub(r'\*(.+?)\*', r'\1', text)               # *italic*
    return text.strip()


def _ascii_safe(text: str) -> str:
    replacements = {
        "–": "-", "—": "-", "―": "-",  # en/em dashes
        "‘": "'", "’": "'",                  # smart single quotes
        "“": '"', "”": '"',                  # smart double quotes
        "…": "...",                               # ellipsis
        " ": " ",                                 # non-breaking space
        "•": "-",                                 # bullet
        "’": "'",                                 # right single quotation
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text


def build_pdf(proposal_text: str, business_name: str, output_dir: str = "./output") -> str:
    proposal_text = _ascii_safe(proposal_text)
    Path(output_dir).mkdir(exist_ok=True)
    safe_name = "".join(c if c.isalnum() else "_" for c in (business_name or "client"))
    filename = f"{output_dir}/proposal_{safe_name}_{date.today().isoformat()}.pdf"

    pdf = ProposalPDF()
    pdf.set_margins(18, 20, 18)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Cover block
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(30, 30, 30)
    pdf.ln(4)
    pdf.cell(0, 12, "Service Proposal", ln=True)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 7, f"Prepared for: {business_name or 'Client'}", ln=True)
    pdf.cell(0, 7, "Prepared by: SouthPeak Systems LLC", ln=True)
    pdf.cell(0, 7, f"Date: {date.today().strftime('%B %d, %Y')}", ln=True)
    pdf.ln(6)
    pdf.set_draw_color(30, 30, 30)
    pdf.line(18, pdf.get_y(), 192, pdf.get_y())
    pdf.ln(8)

    body_w = pdf.w - pdf.l_margin - pdf.r_margin
    indent_w = body_w - 8

    skip_prefixes = ("Prepared for:", "Prepared by:", "Date:", "PROPOSAL HEADER")

    for line in proposal_text.splitlines():
        stripped = _clean_line(line)

        if not stripped:
            pdf.ln(2)
            continue

        if any(stripped.startswith(p) for p in skip_prefixes):
            continue

        # Section headers — start a new page if less than 60mm remains
        if stripped.upper() in SECTION_HEADERS:
            if pdf.get_y() > (pdf.h - pdf.b_margin - 60):
                pdf.add_page()
            else:
                pdf.ln(5)
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(30, 30, 30)
            pdf.cell(body_w, 8, stripped, ln=True)
            pdf.ln(2)
            pdf.set_draw_color(200, 200, 200)
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
            pdf.ln(5)
            continue

        # Bullet lines
        if stripped.startswith("- ") or stripped.startswith("* "):
            pdf.set_x(pdf.l_margin + 6)
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(50, 50, 50)
            pdf.multi_cell(indent_w, 6, f"-  {stripped[2:]}")
            continue

        # Numbered lines
        if len(stripped) > 2 and stripped[0].isdigit() and stripped[1] in ".)":
            pdf.set_x(pdf.l_margin + 6)
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(50, 50, 50)
            pdf.multi_cell(indent_w, 6, stripped)
            continue

        # Timeline labels (bold)
        if any(stripped.startswith(p) for p in TIMELINE_PREFIXES):
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(body_w, 6, stripped)
            continue

        # Body text
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(body_w, 6, stripped)

    pdf.output(filename)
    return filename
