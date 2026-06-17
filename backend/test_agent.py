from dotenv import load_dotenv
load_dotenv(".env.local")

from agent import run_intake_agent
import json

result = run_intake_agent("""
Hi, I run a 12-person HVAC company in Greenville SC.
We're drowning in scheduling calls and follow-up emails.
Our office manager spends 3 hours a day just on this.
Budget is flexible, around $2-3k/month. Need help ASAP.
""")

print(json.dumps(result, indent=2))
