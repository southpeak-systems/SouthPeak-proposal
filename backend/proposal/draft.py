import os
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path


EMAIL_BODY_TEMPLATE = """Hi {business_name},

Thank you for reaching out to SouthPeak Systems. I've put together a proposal based on what you shared — I think we can make a real dent in the time your team is losing to manual work.

I've attached a full proposal outlining the solution, deliverables, pricing, and timeline. Happy to jump on a quick call to walk through it and answer any questions.

Looking forward to connecting.

Brice Gordon
SouthPeak Systems LLC
bgordon@southpeak-systems.com
southpeak-systems.com
"""


def save_draft(
    to_email: str,
    business_name: str,
    pdf_path: str,
    project_type: str,
    output_dir: str = "./output",
) -> str:
    """Save a .eml draft file ready to open in Mail.app and send."""
    Path(output_dir).mkdir(exist_ok=True)

    msg = MIMEMultipart()
    msg["From"] = "bgordon@southpeak-systems.com"
    msg["To"] = to_email
    msg["Subject"] = f"Your Proposal from SouthPeak Systems - {project_type}"

    body = EMAIL_BODY_TEMPLATE.format(
        business_name=business_name or "there",
    )
    msg.attach(MIMEText(body, "plain"))

    with open(pdf_path, "rb") as f:
        attachment = MIMEApplication(f.read(), _subtype="pdf")
        attachment.add_header(
            "Content-Disposition",
            "attachment",
            filename=Path(pdf_path).name,
        )
        msg.attach(attachment)

    safe_name = "".join(c if c.isalnum() else "_" for c in (business_name or "client"))
    draft_path = f"{output_dir}/draft_{safe_name}.eml"
    with open(draft_path, "w") as f:
        f.write(msg.as_string())

    return draft_path
