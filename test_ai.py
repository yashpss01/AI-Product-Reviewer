import os
from sys import path
from test_auth import authenticate_user
from services.ai_summary import summarize_negative_reviews

path.append(os.path.dirname(__file__))

def test_ai_layer():
    print("--- testing phase 5 ai summary ---\n")
    
    # 1. admin level
    print("1. summary for admin (all categories)")
    admin_sum = summarize_negative_reviews(category=None)
    print("admin output:\n")
    print(admin_sum)
    print("\n" + "-"*50 + "\n")
    
    # 2. analyst level
    print("2. summary for analyst (electronics)")
    analyst_sum = summarize_negative_reviews(category="Electronics")
    print("analyst output:\n")
    print(analyst_sum)
    print("\n" + "-"*50 + "\n")
    
if __name__ == "__main__":
    test_ai_layer()
