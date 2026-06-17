from .writer import write_proposal
from .gdoc import create_proposal_doc

def generate_proposal(intake: dict, classification: dict, client_email: str) -> dict:
    """
    Phase 3a: Write proposal and create Google Doc for review.
    Returns doc_id and URL — run approve_proposal.py after editing to finalize.
    """
    proposal_text = write_proposal(intake, classification)

    doc = create_proposal_doc(proposal_text, intake.get("business_name"))

    return {
        "proposal_text": proposal_text,
        "doc_id": doc["doc_id"],
        "doc_url": doc["doc_url"],
        "client_email": client_email,
        "business_name": intake.get("business_name"),
        "project_type": classification.get("project_type", "AI Automation"),
    }
