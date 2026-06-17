import os
from supabase import create_client
from .schema import IntakeAnalysis

def _client():
    return create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_KEY"]
    )

def save_intake(raw_input: str, analysis: IntakeAnalysis) -> str:
    result = _client().table("client_intakes").insert({
        "raw_input": raw_input,
        **analysis.model_dump()
    }).execute()
    return result.data[0]["id"]
