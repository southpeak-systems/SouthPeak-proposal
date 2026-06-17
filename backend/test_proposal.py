from dotenv import load_dotenv
load_dotenv(".env.local")

from intake import process_intake
from agent.hermes import classify_project
from proposal import generate_proposal
import json

intake = process_intake("""
Hi, I run a 12-person HVAC company in Greenville SC.
We're drowning in scheduling calls and follow-up emails.
Our office manager spends 3 hours a day just on this.
Budget is flexible, around $2-3k/month. Need help ASAP.
""")

classification = classify_project(intake)

result = generate_proposal(
    intake=intake,
    classification=classification,
    client_email="owner@hvaccompany.com",
)

print(f"\nGoogle Doc created for review:")
print(f"  URL: {result['doc_url']}")
print(f"  ID:  {result['doc_id']}")
print(f"\nEdit the doc, then run:")
print(f"  .venv/bin/python approve_proposal.py \\")
print(f"    --doc-id {result['doc_id']} \\")
print(f"    --to {result['client_email']} \\")
print(f"    --business \"{result['business_name'] or 'Client'}\" \\")
print(f"    --project-type \"{result['project_type']}\"")
