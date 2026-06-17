"""
Run after reviewing and editing the proposal Google Doc.
Looks up intake record by intake_id — no manual business/email/project-type flags needed.

Usage:
  .venv/bin/python approve_proposal.py --intake-id <UUID>

Or still override manually if needed:
  .venv/bin/python approve_proposal.py --intake-id <UUID> --to override@email.com
"""
from dotenv import load_dotenv
load_dotenv(".env.local")

import argparse, os
from datetime import date
from supabase import create_client

from proposal.gdoc import get_doc_text, export_doc_to_pdf_bytes
from proposal.pdf import build_pdf
from proposal.gmail_draft import create_gmail_draft

parser = argparse.ArgumentParser()
parser.add_argument("--intake-id", required=True, help="UUID from client_intakes table")
parser.add_argument("--to", default=None, help="Override client email")
args = parser.parse_args()

# Look up everything from Supabase
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
row = supabase.table("client_intakes").select(
    "id, business_name, client_email, doc_id, doc_url, project_type"
).eq("id", args.intake_id).single().execute().data

if not row:
    raise SystemExit(f"No intake record found for id: {args.intake_id}")

doc_id       = row["doc_id"]
business     = row["business_name"] or "Client"
client_email = args.to or row["client_email"]
project_type = row["project_type"] or "AI Automation"

if not doc_id:
    raise SystemExit("No doc_id on this intake record — was the proposal generated yet?")
if not client_email:
    raise SystemExit("No client_email on record — pass --to override@email.com")

print(f"Intake:   {args.intake_id}")
print(f"Business: {business}")
print(f"Email:    {client_email}")
print(f"Doc:      {row['doc_url']}")
print()

print("Fetching approved text from Google Doc...")
approved_text = get_doc_text(doc_id)

print("Building local PDF from approved text...")
pdf_path = build_pdf(approved_text, business)
print(f"  PDF saved: {pdf_path}")

print("Exporting Google Doc to PDF for Gmail attachment...")
pdf_bytes = export_doc_to_pdf_bytes(doc_id)
pdf_filename = f"SouthPeak_Proposal_{business.replace(' ', '_')}_{date.today().isoformat()}.pdf"

print("Creating Gmail draft...")
draft_id = create_gmail_draft(
    to_email=client_email,
    business_name=business,
    pdf_bytes=pdf_bytes,
    pdf_filename=pdf_filename,
    project_type=project_type,
)
print(f"  Gmail draft created (ID: {draft_id})")

# Mark intake as approved
supabase.table("client_intakes").update({"status": "approved"}).eq("id", args.intake_id).execute()

print("\nDone. Check your Gmail Drafts folder to review and send.")
