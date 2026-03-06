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
    c.execute('''CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        review_id TEXT UNIQUE,
        product_category TEXT,
        review_text TEXT,
        rating INTEGER,
        date_added TEXT
    )''')
    
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
    
    # Check if we need to initialize default demo users
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        import bcrypt
        print("Initializing default demo users...")
        salt = bcrypt.gensalt()
        admin_hash = bcrypt.hashpw('adminpass'.encode('utf-8'), salt).decode('utf-8')
        c.execute("INSERT INTO users (username, password_hash, role, assigned_category) VALUES (?, ?, ?, ?)", 
                  ('admin_user', admin_hash, 'admin', None))
                  
        analyst_hash = bcrypt.hashpw('analystpass'.encode('utf-8'), salt).decode('utf-8')
        c.execute("INSERT INTO users (username, password_hash, role, assigned_category) VALUES (?, ?, ?, ?)", 
                  ('analyst_electronics', analyst_hash, 'analyst', 'Electronics'))
        conn.commit()
        
    # Check if we need to auto-load dataset
    c.execute("SELECT COUNT(*) FROM reviews")
    is_reviews_empty = c.fetchone()[0] == 0
    
    conn.close()
    
    if is_reviews_empty:
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'cleaned_reviews.csv')
        if os.path.exists(csv_path):
            print("Auto-loading reviews dataset...")
            load_csv_to_db(csv_path)

    print("Database tables ensured.")

def load_csv_to_db(csv_path):
    # load pandas df into sqlite database
    # requires columns: review_id, product_category, review_text, rating, date_added
    print(f"Loading data from {csv_path}...")
    try:
        data = pd.read_csv(csv_path)
        
        conn = get_connection()
        # pandas to_sql makes this way easier
        data.to_sql('reviews', conn, if_exists='append', index=False)
        conn.close()
        
        # print("debug: loaded dataset")
        print(f"successfully loaded {len(data)} records to db.")
    except Exception as e:
        print(f"failed to load csv: {e}")

if __name__ == "__main__":
    # If this file is run directly, setup the db and optionally load data
    setup_database()
