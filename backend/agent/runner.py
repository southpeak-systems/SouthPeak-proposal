from intake import process_intake
from .hermes import classify_project
from .sheets import write_to_sheets

def run_intake_agent(raw_input: str) -> dict:
    # Phase 1: analyze + save to Supabase
    intake_result = process_intake(raw_input)

    # Phase 2a: classify with Hermes
    classification = classify_project(intake_result)

    # Phase 2b: write to Google Sheets
    write_to_sheets(intake_result, classification)

    return {
        "intake": intake_result,
        "classification": classification,
    }
