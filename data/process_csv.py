import pandas as pd
import os

def process_reviews_data(input_csv, output_csv, num_rows=20000):
    print(f"reading {input_csv}")
    
    # just read the first 20k rows so it doesn't crash my laptop
    try:
        df = pd.read_csv(input_csv, nrows=num_rows)
    except FileNotFoundError:
        print("error: cant find the csv file")
        return None
        
    print("loaded", len(df), "rows. cleaning data...")
    
    import random
    categories = ['Electronics', 'Home & Kitchen', 'Books', 'Clothing', 'Beauty & Health']
    
    new_df = pd.DataFrame()
    new_df['review_id'] = df['Id'].astype(str)
    
    # give each product a random category so the charts look better
    unique_products = df['ProductId'].unique()
    product_to_cat = {pid: random.choice(categories) for pid in unique_products}
    
    new_df['product_category'] = df['ProductId'].map(product_to_cat)
    new_df['review_text'] = df['Text']
    new_df['rating'] = df['Score']
    
    # convert unix timestamp to YYYY-MM-DD
    new_df['date_added'] = pd.to_datetime(df['Time'], unit='s').dt.strftime('%Y-%m-%d')
    
    # print(new_df.head()) # checking if it works
    
    new_df.to_csv(output_csv, index=False)
    print("saved to", output_csv)
    
    return output_csv

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    input_file = os.path.join(base_dir, 'Reviews.csv')
    output_file = os.path.join(base_dir, 'cleaned_reviews.csv')
    
    print("processing reviews...")
    cleaned_file = process_reviews_data(input_file, output_file, 20000)
    
    if cleaned_file:
        # push to sqlite
        from sys import path
        path.append(os.path.join(base_dir, '..'))
        
        from database.db import setup_database, load_csv_to_db
        setup_database()
        load_csv_to_db(cleaned_file)
        print("done loading db!")
