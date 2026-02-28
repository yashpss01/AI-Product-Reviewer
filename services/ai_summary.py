import os
from sys import path
from dotenv import load_dotenv

# Optional: if you don't already have openai, pip install openai
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

path.append(os.path.dirname(__file__))
from database.db import get_connection

# Load environment variables from .env
load_dotenv()

def summarize_negative_reviews(category=None):
    # send worst reviews to openai for a quick summary
    if not OpenAI:
        return "Unable to generate AI summary at this time (OpenAI SDK not installed)."
        
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "Unable to generate AI summary at this time (API key missing)."
        
    try:
        conn = get_connection()
        c = conn.cursor()
        
        query = "SELECT review_text FROM reviews WHERE rating <= 2"
        params = []
        
        if category:
            query += " AND product_category = ?"
            params.append(category)
            
        # cap at 50 so we don't blow up the token limit
        query += " LIMIT 50"
        
        c.execute(query, params)
        rows = c.fetchall()
        
        if not rows:
            conn.close()
            return "No negative reviews found to summarize."
            
        reviews_text = []
        for row in rows:
            text = row['review_text']
            # just in case a review is massive
            if len(text) > 500:
                text = text[:500] + "..."
            reviews_text.append(f"- {text}")
            
        conn.close()
        combined_text = "\n".join(reviews_text)
        
        # Initialize OpenAI Client
        client = OpenAI(api_key=api_key)
        
        system_prompt = "You are an analytics assistant summarizing customer complaints."
        user_prompt = f"Here are negative customer reviews. Identify top recurring issues in bullet points. Keep it concise.\n\nReviews:\n{combined_text}"
        
        # Call OpenAI API securely
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3, # Low temperature for more factual, consistent summarization
            max_tokens=250   # Keep the summary concise
        )
        
        summary = response.choices[0].message.content.strip()
        return summary
        
    except Exception as e:
        # fallback if any error happens (like rate limits)
        print("ai error:", e)
        return "Unable to generate AI summary at this time."
