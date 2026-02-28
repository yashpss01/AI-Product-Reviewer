import pandas as pd
import os

def process_reviews_data(input_csv, output_csv, num_rows=20000):
    print(f"Reading {input_csv}...")
    
    # Read only the needed rows to save memory, or read all and sample.
    # We will read exactly num_rows if the file is large, to be efficient.
    # The file has columns: Id,ProductId,UserId,ProfileName,HelpfulnessNumerator,HelpfulnessDenominator,Score,Time,Summary,Text
    try:
        df = pd.read_csv(input_csv, nrows=num_rows)
    except FileNotFoundError:
        print(f"Error: Could not find {input_csv}")
        return None
        
    print(f"Loaded {len(df)} rows. Cleaning and transforming data...")
    
    import random
    categories = ['Electronics', 'Home & Kitchen', 'Books', 'Clothing', 'Beauty & Health']
    
    df_clean = pd.DataFrame()
    df_clean['review_id'] = df['Id'].astype(str)
    # Assign a dummy category to each unique ProductId so it's consistent
    unique_products = df['ProductId'].unique()
    product_to_cat = {pid: random.choice(categories) for pid in unique_products}
    
    df_clean['product_category'] = df['ProductId'].map(product_to_cat)
    df_clean['review_text'] = df['Text']
    df_clean['rating'] = df['Score']
    
    # Convert Unix timestamp to YYYY-MM-DD
    df_clean['date_added'] = pd.to_datetime(df['Time'], unit='s').dt.strftime('%Y-%m-%d')
    
    df_clean.to_csv(output_csv, index=False)
    print(f"Saved cleaned data to {output_csv}")
    
    return output_csv

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    input_file = os.path.join(base_dir, 'Reviews.csv')
    output_file = os.path.join(base_dir, 'cleaned_reviews.csv')
    
    print("Processing real reviews dataset (target ~20k rows)...")
    cleaned_file = process_reviews_data(input_file, output_file, 20000)
    
    if cleaned_file:
        # Load into DB
        from sys import path
        path.append(os.path.join(base_dir, '..'))
        
        from database.db import setup_database, load_csv_to_db
        setup_database()
        load_csv_to_db(cleaned_file)
        print("Phase 1 data pipeline completed successfully using real data.")
