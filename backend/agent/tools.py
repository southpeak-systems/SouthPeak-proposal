from langchain.tools import tool
from intake import process_intake

@tool
def analyze_client_intake(raw_input: str) -> dict:
    """Analyze a client intake submission. Extracts business info, pain points,
    fit score, and recommended service. Saves result to Supabase."""
    return process_intake(raw_input)
