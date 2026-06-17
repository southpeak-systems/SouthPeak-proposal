import os
import hashlib
import requests
from pathlib import Path
from composio_client import Composio


def _upload_pdf_to_composio(pdf_bytes: bytes, filename: str) -> str:
    """Upload PDF bytes to Composio S3 and return the s3key."""
    composio = Composio(api_key=os.environ["COMPOSIO_API_KEY"])

    md5 = hashlib.md5(pdf_bytes).hexdigest()
    presigned = composio.files.create_presigned_url(
        filename=filename,
        md5=md5,
        mimetype="application/pdf",
        tool_slug="GMAIL_CREATE_EMAIL_DRAFT",
        toolkit_slug="gmail",
    )

    upload_url = presigned.new_presigned_url
    s3key = presigned.key

    requests.put(upload_url, data=pdf_bytes).raise_for_status()

    return s3key


EMAIL_BODY = """Hi {business_name},

Thank you for reaching out to SouthPeak Systems. I've put together a proposal based on what you shared — I think we can make a real dent in the time your team is losing to manual work.

I've attached a full proposal outlining the solution, deliverables, pricing, and timeline. Happy to jump on a quick call to walk through it and answer any questions.

Looking forward to connecting.

Brice Gordon
SouthPeak Systems LLC
bgordon@southpeak-systems.com
southpeak-systems.com
"""


def create_gmail_draft(
    to_email: str,
    business_name: str,
    pdf_bytes: bytes,
    pdf_filename: str,
    project_type: str,
) -> str:
    """Create a Gmail draft with the proposal PDF attached. Returns draft ID."""
    composio = Composio(api_key=os.environ["COMPOSIO_API_KEY"])

    s3key = _upload_pdf_to_composio(pdf_bytes, pdf_filename)

    result = composio.tools.execute(
        "GMAIL_CREATE_EMAIL_DRAFT",
        connected_account_id=os.environ["COMPOSIO_GMAIL_ACCOUNT_ID"],
        entity_id=os.environ["COMPOSIO_USER_ID"],
        arguments={
            "recipient_email": to_email,
            "subject": f"Your Proposal from SouthPeak Systems - {project_type}",
            "body": EMAIL_BODY.format(business_name=business_name or "there"),
            "attachment": {
                "name": pdf_filename,
                "mimetype": "application/pdf",
                "s3key": s3key,
            },
        },
    )

    return result.data.get("draft_id") or result.data.get("id") or "created"
