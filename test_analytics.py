import json
import os
from sys import path

path.append(os.path.dirname(__file__))

from services.analytics import (
    calculate_nps,
    get_satisfaction_distribution,
    get_top_products,
    get_worst_products
)

def main():
    print("--- testing phase 2 logic ---\n")
    
    # 1. test nps
    nps_res = calculate_nps()
    print("overall nps data:")
    print(json.dumps(nps_res, indent=2))
    print(f"score: {nps_res['nps']}\n")
    
    # 2. test satisfaction distribution
    sat_res = get_satisfaction_distribution()
    print("satisfaction breakdown:")
    print(json.dumps(sat_res, indent=2))
    print("\n")
    
    # 3. top products
    top = get_top_products(limit=3, min_reviews=20)
    print("top 3 products (min 20 reviews):")
    for idx, p in enumerate(top, 1):
        print(f"  {idx}. {p['product_id']} | avg rating: {p['avg_rating']} | reviews: {p['review_count']}")
    print("\n")
    
    # 4. worst products
    worst = get_worst_products(limit=3, min_reviews=20)
    print("worst 3 products (min 20 reviews):")
    for idx, p in enumerate(worst, 1):
        print(f"  {idx}. {p['product_id']} | avg rating: {p['avg_rating']} | reviews: {p['review_count']}")
    print("\n")
    
if __name__ == "__main__":
    main()
