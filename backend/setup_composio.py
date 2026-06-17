"""
Run this once to authorize Google Sheets via Composio.
It prints an auth URL — open it in your browser and complete the OAuth flow.
"""
from dotenv import load_dotenv
load_dotenv(".env.local")

import os
from composio_client import Composio

COMPOSIO_API_KEY = os.environ["COMPOSIO_API_KEY"]
USER_ID = os.environ.get("COMPOSIO_USER_ID", "southpeak-default")

composio = Composio(api_key=COMPOSIO_API_KEY)

print("Step 1: Creating Google Sheets auth config...")
auth_config = composio.auth_configs.create(
    toolkit={"slug": "googlesheets"},
)
auth_config_id = auth_config.auth_config.id
print(f"  Auth config ID: {auth_config_id}")

print("\nStep 2: Generating authorization link...")
link = composio.link.create(
    auth_config_id=auth_config_id,
    user_id=USER_ID,
)

print("\n" + "=" * 60)
print("OPEN THIS URL IN YOUR BROWSER:")
print(link.redirect_url)
print("=" * 60)
print(f"\nConnected account ID: {link.connected_account_id}")
print("\nAfter completing the Google OAuth flow, add this to your .env.local:")
print(f"  COMPOSIO_CONNECTED_ACCOUNT_ID={link.connected_account_id}")
input("\nPress Enter once you've authorized the account...")
