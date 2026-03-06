import os
from sys import path
import streamlit as st

# Add root directory to path so we can import database
path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.db import get_connection

@st.cache_data(ttl=3600)
def calculate_nps(category=None):
    # figure out the net promoter score
    # promoters = 5, passives = 4, detractors = 1-3
    conn = get_connection()
    c = conn.cursor()
    
    query = "SELECT rating, COUNT(*) as count FROM reviews"
    params = []
    
    if category:
        query += " WHERE product_category = ?"
        params.append(category)
        
    query += " GROUP BY rating"
    
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    
    p_count = 0
    pas_count = 0
    det_count = 0
    
    for row in rows:
        rating = row['rating']
        count = row['count']
        
        if rating == 5:
            p_count += count
        elif rating == 4:
            pas_count += count
        elif rating <= 3:
            det_count += count
            
    tot = p_count + pas_count + det_count
    
    final_nps = 0
    if tot > 0:
        pct_promoters = p_count / tot
        pct_detractors = det_count / tot
        final_nps = round((pct_promoters - pct_detractors) * 100, 2)
        
    return {
        "nps": final_nps,
        "promoters": p_count,
        "passives": pas_count,
        "detractors": det_count,
        "total": tot
    }

@st.cache_data(ttl=3600)
def get_satisfaction_distribution(category=None):
    # group reviews by happy/neutral/unhappy
    conn = get_connection()
    c = conn.cursor()
    
    query = "SELECT rating, COUNT(*) as count FROM reviews"
    params = []
    
    if category:
        query += " WHERE product_category = ?"
        params.append(category)
        
    query += " GROUP BY rating"
    
    c.execute(query, params)
    rows = c.fetchall()
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

@st.cache_data(ttl=3600)
def get_product_rankings(limit=5, min_reviews=10, best=True):
    # rank products based on average rating
    conn = get_connection()
    c = conn.cursor()
    
    sort_dir = "DESC" if best else "ASC"
    
    query = f"""SELECT product_category, COUNT(*) as review_count, AVG(rating) as avg_rating
FROM reviews
GROUP BY product_category
HAVING review_count >= ?
ORDER BY avg_rating {sort_dir}, review_count DESC
LIMIT ?"""
    
    # print(f"running rank query limit {limit}")
    c.execute(query, (min_reviews, limit))
    rows = c.fetchall()
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
    return get_product_rankings(limit, min_reviews, best=True)

def get_worst_products(limit=5, min_reviews=10):
    return get_product_rankings(limit, min_reviews, best=False)

@st.cache_data(ttl=3600)
def get_all_categories():
    # grab all unique product categories
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT DISTINCT product_category FROM reviews WHERE product_category IS NOT NULL ORDER BY product_category")
    rows = c.fetchall()
    conn.close()
    return [row['product_category'] for row in rows]
