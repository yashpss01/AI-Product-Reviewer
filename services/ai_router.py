import os
import json
from sys import path
from dotenv import load_dotenv

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

path.append(os.path.dirname(__file__))

# Load environment variables
load_dotenv()

def parse_query_intent(query):
    # have openai figure out what the user wants based on the string

    if not OpenAI:
        return {"error": "OpenAI SDK not installed"}
        
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"error": "API key missing"}
        
    try:
        client = OpenAI(api_key=api_key)
        
        system_prompt = """
You are a query classifier for a product reviews analytics system. 
Respond ONLY in valid JSON. Do not explain anything. Do not use Markdown formatting for the JSON.

Available actions:
- "calculate_nps"
- "satisfaction_distribution"
- "top_products"
- "worst_products"
- "complaint_summary" (e.g., "why are customers unhappy", "summarize complaints")
- "unknown" (if none of the above match)

Extract parameters:
- "category": (string or null) The specific product category mentioned.
- "limit": (integer or null) The number of products to return if ranking.

JSON Format:
{"action": "action_name", "category": null, "limit": null}
"""
        
        user_prompt = f"Classify this query: '{query}'"
        
        # send prompt
        res = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,
            response_format={"type": "json_object"} # force strict json
        )
        
        raw_text = res.choices[0].message.content.strip()
        parsed = json.loads(raw_text)
        
        # fallback action if it missed it
        if "action" not in parsed:
            parsed["action"] = "unknown"
            
        return parsed
        
    except Exception as e:
        print(f"router error: {e}")
        
        # fallback just in case openai quota blocks us during the demo
        lower_q = query.lower()
        if "nps" in lower_q:
            return {"action": "calculate_nps", "category": None, "limit": None}
        elif "satisfaction" in lower_q:
            return {"action": "satisfaction_distribution", "category": None, "limit": None}
        elif "top" in lower_q or "best" in lower_q:
            return {"action": "top_products", "category": None, "limit": 5}
        elif "worst" in lower_q or "bad" in lower_q:
            return {"action": "worst_products", "category": None, "limit": 5}
        elif "why" in lower_q or "complaint" in lower_q or "unhappy" in lower_q:
            return {"action": "complaint_summary", "category": None, "limit": None}
            
        return {"error": "Failed to parse query intent."}
