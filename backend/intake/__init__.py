from .analyzer import analyze_intake
from .storage import save_intake

def process_intake(raw_input: str) -> dict:
    analysis = analyze_intake(raw_input)
    record_id = save_intake(raw_input, analysis)
    return {"id": record_id, **analysis.model_dump()}
