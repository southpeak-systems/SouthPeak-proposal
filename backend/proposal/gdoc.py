import os
import re
from composio_client import Composio
from datetime import date


SECTION_HEADERS = {
    "EXECUTIVE SUMMARY", "THE CHALLENGE", "OUR PROPOSED SOLUTION",
    "WHAT YOU GET", "INVESTMENT", "TIMELINE", "NEXT STEPS", "CLOSING"
}

def _strip_bold(text: str) -> str:
    return re.sub(r'\*\*(.+?)\*\*', r'\1', text)


def _to_markdown(proposal_text: str) -> str:
    """Convert plain proposal text to clean markdown for Google Docs."""
    content_lines = []  # only real content, no blank lines — we add those at the end
    numbered_counter = 0

    for line in proposal_text.splitlines():
        line = re.sub(r'^#{1,6}\s*', '', line)
        stripped = line.strip()

        if not stripped:
            numbered_counter = 0
            continue

        if stripped.upper() in SECTION_HEADERS:
            content_lines.append(("header", stripped))
            numbered_counter = 0
            continue

        num_match = re.match(r'^(\d+)[.)]\s+(.*)', stripped)
        if num_match:
            numbered_counter += 1
            content_lines.append(("numbered", f"{numbered_counter})  {_strip_bold(num_match.group(2))}"))
            continue

        if not re.match(r'^\d+[.)]', stripped):
            numbered_counter = 0

        if stripped.startswith("- ") or stripped.startswith("* "):
            content_lines.append(("bullet", f"•  {_strip_bold(stripped[2:])}"))
            continue

        content_lines.append(("body", _strip_bold(stripped)))

    # Now assemble with guaranteed blank line after every item
    lines = []
    for kind, text in content_lines:
        if kind == "header":
            lines.append(f"## {text}")
        else:
            lines.append(text)
        lines.append("")  # blank line after every single item, no exceptions

    # Remove final trailing blank
    while lines and lines[-1] == "":
        lines.pop()

    markdown = "\n".join(lines)
    print("\n=== MARKDOWN SENT TO GOOGLE DOCS ===")
    print(markdown)
    print("=== END MARKDOWN ===\n")
    return markdown


def create_proposal_doc(proposal_text: str, business_name: str) -> dict:
    """Create a Google Doc with the proposal content. Returns doc_id and URL."""
    composio = Composio(api_key=os.environ["COMPOSIO_API_KEY"])
    connected_account_id = os.environ["COMPOSIO_GOOGLEDOCS_ACCOUNT_ID"]
    user_id = os.environ["COMPOSIO_USER_ID"]

    title = f"Proposal - {business_name or 'Client'} - {date.today().strftime('%B %d, %Y')}"
    markdown = _to_markdown(proposal_text)

    result = composio.tools.execute(
        "GOOGLEDOCS_CREATE_DOCUMENT_MARKDOWN",
        connected_account_id=connected_account_id,
        entity_id=user_id,
        arguments={
            "title": title,
            "markdown_text": markdown,
        },
    )

    data = result.data
    doc_id = data.get("document_id") or data.get("documentId") or data.get("id")
    doc_url = (
        data.get("document_url")
        or data.get("url")
        or f"https://docs.google.com/document/d/{doc_id}/edit"
    )

    return {"doc_id": doc_id, "doc_url": doc_url, "title": title}


def get_doc_text(doc_id: str) -> str:
    """Pull the current plaintext content from a Google Doc."""
    composio = Composio(api_key=os.environ["COMPOSIO_API_KEY"])

    result = composio.tools.execute(
        "GOOGLEDOCS_GET_DOCUMENT_PLAINTEXT",
        connected_account_id=os.environ["COMPOSIO_GOOGLEDOCS_ACCOUNT_ID"],
        entity_id=os.environ["COMPOSIO_USER_ID"],
        arguments={"document_id": doc_id},
    )
    return result.data.get("plaintext") or result.data.get("text") or ""


def export_doc_to_pdf_bytes(doc_id: str) -> bytes:
    """Export a Google Doc to PDF and return the raw bytes."""
    import requests
    composio = Composio(api_key=os.environ["COMPOSIO_API_KEY"])

    result = composio.tools.execute(
        "GOOGLEDOCS_EXPORT_DOCUMENT_AS_PDF",
        connected_account_id=os.environ["COMPOSIO_GOOGLEDOCS_ACCOUNT_ID"],
        entity_id=os.environ["COMPOSIO_USER_ID"],
        arguments={"file_id": doc_id},
    )

    s3url = result.data["download_url"]["s3url"]
    response = requests.get(s3url)
    response.raise_for_status()
    return response.content
