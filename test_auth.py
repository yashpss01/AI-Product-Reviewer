import os
from sys import path

path.append(os.path.dirname(__file__))

from database.db import setup_database
from services.auth import create_user, authenticate_user, get_user_accessible_category

def test_auth():
    print("--- Testing Phase 3 Auth Logic ---\n")
    
    # Ensure tables exist
    setup_database()
    
    print("\n1. Seeding Admin User...")
    admin_created = create_user("admin_user", "adminpass", "admin")
    if admin_created:
        print(" -> Admin created successfully.")
    else:
        print(" -> Admin already exists (or failed).")
        
    print("\n2. Seeding Analyst User...")
    analyst_created = create_user("analyst_electronics", "analystpass", "analyst", "Electronics")
    if analyst_created:
        print(" -> Analyst created successfully.")
    else:
        print(" -> Analyst already exists (or failed).")
        
    print("\n3. Testing Duplicate User Creation...")
    dup_created = create_user("admin_user", "newpass123", "admin")
    if not dup_created:
        print(" -> SUCCESS: Duplicate username prevented properly.")
    else:
        print(" -> FAIL: Duplicate username was allowed!")
        
    print("\n4. Testing Login Success...")
    admin_auth = authenticate_user("admin_user", "adminpass")
    if admin_auth:
        print(f" -> SUCCESS: Admin logged in! User data: {admin_auth}")
    else:
        print(" -> FAIL: Admin login failed.")
        
    analyst_auth = authenticate_user("analyst_electronics", "analystpass")
    if analyst_auth:
        print(f" -> SUCCESS: Analyst logged in! User data: {analyst_auth}")
    else:
        print(" -> FAIL: Analyst login failed.")
        
    print("\n5. Testing Login Failure (wrong password)...")
    bad_auth = authenticate_user("admin_user", "wrongpassword")
    if not bad_auth:
        print(" -> SUCCESS: Wrong password rejected.")
    else:
        print(" -> FAIL: Wrong password was accepted!")
        
    print("\n6. Testing Role Accessibility...")
    admin_cat = get_user_accessible_category(admin_auth)
    print(f" -> Admin category limit: {admin_cat} (Expect None)")
    
    analyst_cat = get_user_accessible_category(analyst_auth)
    print(f" -> Analyst category limit: {analyst_cat} (Expect 'Electronics')")

if __name__ == "__main__":
    test_auth()
