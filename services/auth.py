import sqlite3
import bcrypt
import os
from sys import path

# Add root directory to path so we can import database
path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.db import get_connection

def hash_password(password):
    # secure the password before saving
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_user(username, password, role, assigned_category=None):
    # create new user, return false if username is taken
    conn = get_connection()
    c = conn.cursor()
    
    # make sure they aren't already in the db
    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    if c.fetchone() is not None:
        conn.close()
        return False
        
    h_pwd = hash_password(password)
    
    try:
        c.execute("""INSERT INTO users 
            (username, password_hash, role, assigned_category) 
            VALUES (?, ?, ?, ?)""",
            (username, h_pwd, role, assigned_category))
        conn.commit()
        # print("created user ok")
        success = True
    except sqlite3.IntegrityError:
        success = False # just in case
    finally:
        conn.close()
        
    return success

def authenticate_user(username, password):
    # check credentials
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return None
        
    if check_password(password, row['password_hash']):
        return dict(row) # convert row to dictionary
        
    return None

def get_user_accessible_category(user):
    # figure out if the user can see everything or just one category
    if not user:
        return None
        
    r = user.get("role")
    if r == "admin":
        return None
    elif r == "analyst":
        return user.get("assigned_category")
        
    return None
