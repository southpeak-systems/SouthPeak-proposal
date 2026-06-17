from dotenv import load_dotenv
load_dotenv(".env.local")

from intake import process_intake
import json

result = process_intake("""
Hi, I run a 12-person HVAC company in Greenville SC.
We're drowning in scheduling calls and follow-up emails.
Our office manager spends 3 hours a day just on this.
Budget is flexible, around $2-3k/month. Need help ASAP.
""")

print(json.dumps(result, indent=2))
