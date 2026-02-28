import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'reviews.db')

def get_connection():
    # connect to our local sqlite db
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us get columns by name later
    return conn

def setup_database():
    conn = get_connection()
    c = conn.cursor()
    
    # reviews table
    c.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review_id TEXT UNIQUE,
            product_category TEXT,
            review_text TEXT,
            rating INTEGER,
            date_added TEXT
        )
    ''')
    
    # authentication
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            assigned_category TEXT
        )
    ''')
    
    # tracking past queries
    c.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            query_text TEXT NOT NULL,
            result_summary TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database tables ensured.")

def load_csv_to_db(csv_path):
    """
    Loads data from a cleaned CSV file into the SQLite database.
    Expects columns: review_id, product_category, review_text, rating, date_added
    """
    print(f"Loading data from {csv_path}...")
    try:
        df = pd.read_csv(csv_path)
        
        conn = get_connection()
        # pandas to_sql is an easy way to load a dataframe to a sqlite table
        # if_exists='append' will add to existing data
        # We drop the dataframe index so it doesn't create an 'index' column in SQLite
        df.to_sql('reviews', conn, if_exists='append', index=False)
        conn.close()
        
        print(f"Successfully loaded {len(df)} records into the database.")
    except Exception as e:
        print(f"Error loading CSV to database: {e}")

if __name__ == "__main__":
    # If this file is run directly, setup the db and optionally load data
    setup_database()
