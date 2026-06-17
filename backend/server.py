"""
FastAPI server — receives intake submissions from the Next.js frontend,
runs the full pipeline (intake → Hermes classification → Sheets → Google Doc),
and sends an internal notification email to Brice.
"""
from dotenv import load_dotenv
load_dotenv(".env.local")

from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from supabase import create_client
import os
import traceback

from intake import process_intake

app = FastAPI()

supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])


class IntakeRequest(BaseModel):
    raw_input: str
    client_email: str
    business_name: str


@app.post("/intake")
async def run_intake(req: IntakeRequest, background_tasks: BackgroundTasks):
    # Return immediately — entire pipeline runs in background
    background_tasks.add_task(
        _run_pipeline,
        raw_input=req.raw_input,
        client_email=req.client_email,
        business_name=req.business_name,
    )
    return JSONResponse({"success": True})


def _run_pipeline(raw_input: str, client_email: str, business_name: str):
    from agent.hermes import classify_project
    from agent.sheets import write_to_sheets
    from proposal import generate_proposal

    try:
        intake = process_intake(raw_input)
    except Exception:
        print("[pipeline] ERROR in intake analysis:")
        traceback.print_exc()
        return

    try:
        supabase.table("client_intakes").update({
            "client_email": client_email,
            "business_name": business_name or intake.get("business_name"),
        }).eq("id", intake["id"]).execute()
        if business_name:
            intake["business_name"] = business_name
    except Exception:
        print("[pipeline] ERROR persisting form fields to Supabase:")
        traceback.print_exc()

    try:
        classification = classify_project(intake)
    except Exception:
        print("[pipeline] ERROR in Hermes classification:")
        traceback.print_exc()
        return

    try:
        write_to_sheets(intake, classification)
    except Exception:
        print("[pipeline] ERROR writing to Google Sheets:")
        traceback.print_exc()

    try:
        result = generate_proposal(
            intake=intake,
            classification=classification,
            client_email=client_email,
        )
    except Exception:
        print("[pipeline] ERROR generating proposal:")
        traceback.print_exc()
        return

    try:
        supabase.table("client_intakes").update({
            "doc_id": result["doc_id"],
            "doc_url": result["doc_url"],
            "project_type": classification.get("project_type"),
        }).eq("id", intake["id"]).execute()
    except Exception:
        print("[pipeline] ERROR updating Supabase with doc info:")
        traceback.print_exc()

    try:
        _notify_brice(
            intake_id=intake["id"],
            business_name=business_name or intake.get("business_name") or "Unknown",
            client_email=client_email,
            project_type=classification.get("project_type", ""),
            tier=classification.get("tier", ""),
            price=classification.get("price_output", ""),
            doc_url=result["doc_url"],
        )
    except Exception:
        print("[pipeline] ERROR sending notification email:")
        traceback.print_exc()


def _notify_brice(
    intake_id: str,
    business_name: str,
    client_email: str,
    project_type: str,
    tier: str,
    price: str,
    doc_url: str,
):
    from composio_client import Composio

    composio = Composio(api_key=os.environ["COMPOSIO_API_KEY"])

    body = f"""New intake submission received.

Business: {business_name}
Client email: {client_email}
Project type: {project_type}
Tier: {tier}
Price: {price}

Review and edit the proposal draft here:
{doc_url}

Once approved, run:
  cd ~/southpeak-systems/backend && .venv/bin/python approve_proposal.py --intake-id {intake_id}
"""

    composio.tools.execute(
        "GMAIL_SEND_EMAIL",
        connected_account_id=os.environ["COMPOSIO_GMAIL_ACCOUNT_ID"],
        entity_id=os.environ["COMPOSIO_USER_ID"],
        arguments={
            "recipient_email": "bgordon@southpeak-systems.com",
            "subject": f"New proposal ready for review — {business_name}",
            "body": body,
        },
    )


@app.get("/health")
def health():
    return {"status": "ok"}
