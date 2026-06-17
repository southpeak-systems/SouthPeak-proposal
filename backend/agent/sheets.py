import os
from composio_client import Composio

def _composio_client() -> Composio:
    return Composio(api_key=os.environ["COMPOSIO_API_KEY"])

def write_to_sheets(intake_result: dict, classification: dict) -> None:
    """Append a row to the Google Sheet with intake + classification data."""
    composio = Composio(api_key=os.environ["COMPOSIO_API_KEY"])
    connected_account_id = os.environ["COMPOSIO_CONNECTED_ACCOUNT_ID"]
    spreadsheet_id = os.environ["GOOGLE_SHEET_ID"]

    price_display = classification.get("price_output", "")
    if classification.get("estimated_hours"):
        price_display = f"{classification['estimated_hours']} → {price_display}"
    if classification.get("scope_review_note"):
        price_display = f"{price_display} *"

    retainer_applies = classification.get("retainer_applies", False)
    retainer_yn = "Yes" if retainer_applies else "No"
    retainer_price = classification.get("retainer_price", "") if retainer_applies else ""

    # Column order: ID, Business, Industry, Urgency, Fit Score, Service, Budget,
    #               Project Type, Tier, Price Range, Retainer, Retainer Price, Reasoning, Summary
    row = [
        intake_result.get("id", ""),
        intake_result.get("business_name", ""),
        intake_result.get("industry", ""),
        intake_result.get("urgency", ""),
        str(intake_result.get("fit_score", "")),
        intake_result.get("recommended_service", ""),
        intake_result.get("budget_range", ""),
        classification.get("project_type", ""),
        classification.get("tier", ""),
        price_display,
        retainer_yn,
        retainer_price,
        classification.get("reasoning", ""),
        intake_result.get("summary", ""),
    ]


    composio.tools.execute(
        "GOOGLESHEETS_SPREADSHEETS_VALUES_APPEND",
        connected_account_id=connected_account_id,
        entity_id=os.environ["COMPOSIO_USER_ID"],
        arguments={
            "spreadsheetId": spreadsheet_id,
            "range": "Sheet1!A:N",
            "values": [row],
            "valueInputOption": "RAW",
            "insertDataOption": "INSERT_ROWS",
        },
    )
