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
    print("--- Testing Phase 2 Logic ---\n")
    
    # 1. Test NPS
    nps_data = calculate_nps()
    print("Aggregate NPS Data:")
    print(json.dumps(nps_data, indent=2))
    print(f"Calculated NPS Score: {nps_data['nps']}\n")
    
    # 2. Test Satisfaction Distribution
    sat_data = get_satisfaction_distribution()
    print("Satisfaction Distribution:")
    print(json.dumps(sat_data, indent=2))
    print("\n")
    
    # 3. Test Top Products (limit 3, min reviews 10)
    top_products = get_top_products(limit=3, min_reviews=20)
    print("Top 3 Products (Min 20 reviews):")
    for idx, p in enumerate(top_products, 1):
        print(f"  {idx}. {p['product_id']} | Avg Rating: {p['avg_rating']} | Reviews: {p['review_count']}")
    print("\n")
    
    # 4. Test Worst Products (limit 3, min reviews 10)
    worst_products = get_worst_products(limit=3, min_reviews=20)
    print("Worst 3 Products (Min 20 reviews):")
    for idx, p in enumerate(worst_products, 1):
        print(f"  {idx}. {p['product_id']} | Avg Rating: {p['avg_rating']} | Reviews: {p['review_count']}")
    print("\n")
    
if __name__ == "__main__":
    main()
