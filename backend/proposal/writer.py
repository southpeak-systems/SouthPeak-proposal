import anthropic
from pathlib import Path
from jinja2 import Template

client = anthropic.Anthropic()

TEMPLATE_PATH = Path(__file__).parent / "templates" / "proposal.txt"

def write_proposal(intake: dict, classification: dict) -> str:
    """Have Claude write the full proposal text from intake + classification."""
    template = Template(TEMPLATE_PATH.read_text())

    prompt = template.render(
        business_name=intake.get("business_name") or "the client",
        industry=intake.get("industry") or "their industry",
        pain_points=", ".join(intake.get("pain_points") or []),
        summary=intake.get("summary") or "",
        project_type=classification.get("project_type") or "",
        tier=classification.get("tier") or "",
        price_output=classification.get("price_output") or "",
        estimated_hours=classification.get("estimated_hours"),
        scope_review_note=classification.get("scope_review_note"),
        retainer_applies=classification.get("retainer_applies", False),
        retainer_price=classification.get("retainer_price") or "",
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text.strip()
