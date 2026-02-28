import os
from sys import path
from test_auth import authenticate_user
from services.ai_router import parse_query_intent

path.append(os.path.dirname(__file__))

def test_ai_router():
    print("--- Testing Phase 6 AI Router ---\n")
    
    queries = [
        "What is the NPS for Electronics?",
        "Show NPS for Books",
        "Show top 3 products",
        "Why are customers unhappy?",
        "How is the satisfaction distribution?",
        "Summarize complaints about Home & Kitchen"
    ]
    
    for q in queries:
        print(f"User Query: '{q}'")
        intent = parse_query_intent(q)
        print(f"-> Parsed Intent: {intent}")
        print("-" * 50)
    
if __name__ == "__main__":
    test_ai_router()
