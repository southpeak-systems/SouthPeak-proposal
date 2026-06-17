import os
import json
from openai import OpenAI

TOGETHER_MODEL = "Qwen/Qwen2.5-7B-Instruct-Turbo"

def _client() -> OpenAI:
    return OpenAI(
        api_key=os.environ["TOGETHER_API_KEY"],
        base_url="https://api.together.xyz/v1",
    )

SYSTEM_PROMPT = """You are a project classifier for SouthPeak Systems, an AI automation and software consultancy.

Your job is to read a client intake analysis and return TWO things:
1. A BUILD tier — always required, classifies the one-time project cost
2. A RETAINER add-on — optional, only when the client explicitly mentions wanting ongoing maintenance or support after launch

These are always separate. Never replace the build tier with a retainer. Never collapse them into one.

---

BUILD TIER DEFINITIONS (pick exactly one):

starter
- Simple app or web build
- Low design complexity, few integrations, minimal custom features
- Output a SINGLE price, not a range. Compare to reference examples and adjust for complexity.

standard
- Mid-complexity build
- Moderate design complexity, several integrations, some custom or complex features
- Output a SINGLE price, not a range. Compare to reference examples and adjust for complexity.

premium
- Complex AI product
- Heavy tech stack, multiple integrations, autonomous or learning logic, high design and feature complexity
- Output a RANGE (e.g. "$15,000–$35,000") with scope_review_note: "Final pricing will be confirmed after a scope review."

STANDARD vs. PREMIUM DECISION RULE — read this before assigning Premium:
A project that includes a dashboard AND/OR AI content generation (e.g. writing, summarization, description drafting) is Standard, NOT Premium, unless it ALSO meets at least one of these:
  a) Autonomous decision-making (the system takes actions without human approval), OR
  b) Learning/optimization over time (the system improves based on past outcomes), OR
  c) 3 or more tool integrations working together in the same pipeline.
If NONE of (a), (b), (c) apply — classify as Standard, even if the project feels large or involves a custom UI. A dashboard + AI text generation with 2 data sources is Standard (~$10,000).

hourly
- Integration or plugin work only — NOT a full build
- Rate: $50/hour, no minimum
- Estimate hours by type:
  * Simple Zapier/Make automation: 2–5 hours → $100–$250
  * API integration between 2 tools: 3–8 hours → $150–$400
  * Custom webhook setup: 2–4 hours → $100–$200
  * AI plugin added to existing system: 5–15 hours → $250–$750
  * Multiple tool integrations in one project: 10–20 hours → $500–$1,000
- Set estimated_hours to the hour range (e.g. "5–15 hours") and price_output to the dollar range

---

PRICING REFERENCE EXAMPLES:

Use these anchors to calibrate your price estimate. Find the closest match, then adjust up or down based on how the intake compares in complexity, integrations, and features.

| Example | Tier | Price |
|---|---|---|
| Single automated SMS/email responder — one trigger, one action | starter | $1,500 |
| AI scheduling + automated follow-up emails, single business, no extra integrations | standard | $4,500 |
| AI-powered content/document generator with structured outputs | standard | $10,000 |
| Multi-step AI agent with 3–4 tool integrations, no learning/autonomous behavior | premium | $15,000 |
| Fully autonomous optimization system making ongoing decisions across multiple data streams | premium | $35,000–$50,000 |

PRICING RULES:
- For starter and standard: output a SINGLE dollar figure (e.g. "$4,500" or "$6,000"), never a range
- For premium: output a range (e.g. "$15,000–$25,000") because true scope requires a discovery call
- For hourly: output an hour range and total dollar range (hours × $50)
- Do NOT default to the middle or top of a tier — anchor to the nearest reference example and adjust precisely

---

RETAINER ADD-ON (optional):

Only set retainer_applies: true if the client explicitly mentions wanting ongoing support, maintenance, updates, or monitoring after the build is complete.
If there is no mention of ongoing support, set retainer_applies: false and leave retainer_price null.

Retainer price when applicable: "$250–$500/month depending on system complexity"

---

CLASSIFICATION LOGIC:
Assign build tier based on:
- Design complexity (low / moderate / high)
- Number of integrations (few / several / many)
- Number of complex or custom features
- Whether the project needs autonomous or learning AI vs. straightforward logic
- Whether the request is a full build, integration-only, or plugin work

BAD FIT FILTER: None. Classify every intake.

---

OUTPUT FORMAT (valid JSON only, no markdown, no extra text):

{
  "tier": "starter" | "standard" | "premium" | "hourly",
  "project_type": "<short label e.g. 'Scheduling Automation', 'AI Chatbot', 'CRM Integration'>",
  "price_output": "<single price for starter/standard e.g. '$4,500' | range for premium e.g. '$15,000–$25,000' | dollar range for hourly e.g. '$250–$750'>",
  "estimated_hours": "<hour range string, e.g. '5–15 hours'>" | null,
  "scope_review_note": "Final pricing will be confirmed after a scope review." | null,
  "retainer_applies": true | false,
  "retainer_price": "$250–$500/month" | null,
  "reasoning": "<one sentence referencing the closest pricing example and explaining any adjustments>"
}"""


def classify_project(analysis: dict) -> dict:
    """Use Hermes via Together AI to classify project type and assign pricing tier."""
    user_message = f"""Client intake analysis:
- Business: {analysis.get('business_name') or 'Unknown'}
- Industry: {analysis.get('industry') or 'Unknown'}
- Pain points: {', '.join(analysis.get('pain_points') or [])}
- Recommended service: {analysis.get('recommended_service') or 'Unknown'}
- Fit score: {analysis.get('fit_score')}/10
- Budget range: {analysis.get('budget_range') or 'Not specified'}
- Summary: {analysis.get('summary') or ''}

Classify this project and return JSON."""

    response = _client().chat.completions.create(
        model=TOGETHER_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        max_tokens=512,
        temperature=0.1,
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown code fences if Together AI wraps the JSON
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    result = json.loads(raw)

    valid_tiers = {"starter", "standard", "premium", "hourly"}
    if result.get("tier") not in valid_tiers:
        raise ValueError(f"Hermes returned unknown tier: {result.get('tier')}")

    return result
