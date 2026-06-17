"""
One-time authorization for Gmail and Google Docs via Composio.
Run this script, open each URL in your browser, and complete OAuth for both.
"""
from dotenv import load_dotenv
load_dotenv(".env.local")

import os
from composio_client import Composio

COMPOSIO_API_KEY = os.environ["COMPOSIO_API_KEY"]
USER_ID = os.environ.get("COMPOSIO_USER_ID", "southpeak-default")

composio = Composio(api_key=COMPOSIO_API_KEY)

TOOLKITS = [
    ("gmail", "COMPOSIO_GMAIL_ACCOUNT_ID"),
    ("googledocs", "COMPOSIO_GOOGLEDOCS_ACCOUNT_ID"),
]

results = {}

for slug, env_key in TOOLKITS:
    print(f"\n{'='*60}")
    print(f"Authorizing: {slug.upper()}")
    print(f"{'='*60}")

    auth_config = composio.auth_configs.create(
        toolkit={"slug": slug},
    )
    auth_config_id = auth_config.auth_config.id
    print(f"Auth config ID: {auth_config_id}")

    link = composio.link.create(
        auth_config_id=auth_config_id,
        user_id=USER_ID,
    )

    print(f"\nOPEN THIS URL IN YOUR BROWSER:")
    print(link.redirect_url)
    print(f"\nConnected account ID (save this): {link.connected_account_id}")
    input(f"\nComplete the {slug} OAuth flow, then press Enter...")

    results[env_key] = link.connected_account_id
    print(f"Saved: {env_key}={link.connected_account_id}")

print("\n" + "="*60)
print("Add these to your .env.local:")
for key, val in results.items():
    print(f"  {key}={val}")
print("="*60)
