import anthropic
import json
from .schema import IntakeAnalysis

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are a business analyst for SouthPeak Systems, an AI automation consultancy in South Carolina.
Analyze client intake submissions and extract structured data.
Respond ONLY with valid JSON — no markdown, no code fences, no extra text."""

def analyze_intake(raw_input: str) -> IntakeAnalysis:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""Analyze this client intake and return JSON with these exact fields:
- business_name (string or null)
- industry (string or null)
- pain_points (array of strings)
- budget_range (string or null, e.g. "$2k-$3k/month")
- urgency ("low", "medium", or "high")
- fit_score (integer 1-10, how well suited for AI automation)
- recommended_service (e.g. "AI Email Automation", "Process Automation", "Custom Dashboard")
- summary (2-3 sentence plain-English overview)

Intake submission:
{raw_input}"""
        }]
    )

    data = json.loads(response.content[0].text)
    return IntakeAnalysis(**data)
