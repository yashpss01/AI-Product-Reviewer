import os
from sys import path

# Add root directory to path so we can import database
path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.db import get_connection

def calculate_nps(category=None):
    """
    Calculates the Net Promoter Score (NPS) based on ratings.
    Promoters: 5
    Passives: 4
    Detractors: 1, 2, 3
    
    Returns a dictionary with raw counts and the final NPS score.
    NPS = (% Promoters - % Detractors) * 100
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT rating, COUNT(*) as count FROM reviews"
    params = []
    
    if category:
        query += " WHERE product_category = ?"
        params.append(category)
        
    query += " GROUP BY rating"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    promoters = 0
    passives = 0
    detractors = 0
    
    for row in rows:
        rating = row['rating']
        count = row['count']
        
        if rating == 5:
            promoters += count
        elif rating == 4:
            passives += count
        elif rating <= 3:
            detractors += count
            
    total = promoters + passives + detractors
    
    nps_score = 0
    if total > 0:
        pct_promoters = promoters / total
        pct_detractors = detractors / total
        nps_score = round((pct_promoters - pct_detractors) * 100, 2)
        
    return {
        "nps": nps_score,
        "promoters": promoters,
        "passives": passives,
        "detractors": detractors,
        "total": total
    }

def get_satisfaction_distribution(category=None):
    """
    Returns counts of reviews categorized by satisfaction level:
    Happy: 4, 5
    Neutral: 3
    Unhappy: 1, 2
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT rating, COUNT(*) as count FROM reviews"
    params = []
    
    if category:
        query += " WHERE product_category = ?"
        params.append(category)
        
    query += " GROUP BY rating"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    happy = 0
    neutral = 0
    unhappy = 0
    
    for row in rows:
        rating = row['rating']
        count = row['count']
        
        if rating >= 4:
            happy += count
        elif rating == 3:
            neutral += count
        else:
            unhappy += count
            
    return {
        "Happy": happy,
        "Neutral": neutral,
        "Unhappy": unhappy
    }

def get_product_rankings(limit=5, min_reviews=10, best=True):
    """
    Helper function to get top or worst products based on average rating.
    Only considers products with at least `min_reviews`.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    order_direction = "DESC" if best else "ASC"
    
    query = f"""
        SELECT 
            product_category,
            COUNT(*) as review_count,
            AVG(rating) as avg_rating
        FROM reviews
        GROUP BY product_category
        HAVING review_count >= ?
        ORDER BY avg_rating {order_direction}, review_count DESC
        LIMIT ?
    """
    
    cursor.execute(query, (min_reviews, limit))
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        results.append({
            "product_id": row['product_category'], # In our dataset, product_category stores the ProductId
            "avg_rating": round(row['avg_rating'], 2),
            "review_count": row['review_count']
        })
        
    return results

def get_top_products(limit=5, min_reviews=10):
    """Returns the top `limit` products with at least `min_reviews` reviews."""
    return get_product_rankings(limit, min_reviews, best=True)

def get_worst_products(limit=5, min_reviews=10):
    """Returns the worst `limit` products with at least `min_reviews` reviews."""
    return get_product_rankings(limit, min_reviews, best=False)

def get_all_categories():
    """Returns a list of all distinct product categories."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT product_category FROM reviews WHERE product_category IS NOT NULL ORDER BY product_category")
    rows = cursor.fetchall()
    conn.close()
    return [row['product_category'] for row in rows]
