import os
from sys import path
from test_auth import authenticate_user
from services.ai_summary import summarize_negative_reviews

path.append(os.path.dirname(__file__))

def test_ai_layer():
    print("--- Testing Phase 5 AI Summarization ---\n")
    
    # 1. Admin Level
    print("1. Testing AI Summary for Admin (All Categories)")
    admin_summary = summarize_negative_reviews(category=None)
    print("Admin Summary Output:\n")
    print(admin_summary)
    print("\n" + "-"*50 + "\n")
    
    # 2. Analyst Level
    print("2. Testing AI Summary for Analyst (Electronics only)")
    analyst_summary = summarize_negative_reviews(category="Electronics")
    print("Analyst (Electronics) Summary Output:\n")
    print(analyst_summary)
    print("\n" + "-"*50 + "\n")
    
if __name__ == "__main__":
    test_ai_layer()
