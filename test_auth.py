import os
from sys import path

path.append(os.path.dirname(__file__))

from database.db import setup_database
from services.auth import create_user, authenticate_user, get_user_accessible_category

def test_auth():
    print("--- testing phase 3 auth ---\n")
    
    # make sure tables are there
    setup_database()
    
    print("\n1. seeding admin user...")
    admin_created = create_user("admin_user", "adminpass", "admin")
    if admin_created:
        print(" -> admin created ok.")
    else:
        print(" -> admin already exists.")
        
    print("\n2. seeding analyst user...")
    analyst_created = create_user("analyst_electronics", "analystpass", "analyst", "Electronics")
    if analyst_created:
        print(" -> analyst created ok.")
    else:
        print(" -> analyst already exists.")
        
    print("\n3. testing duplicates...")
    dup_created = create_user("admin_user", "newpass123", "admin")
    if not dup_created:
        print(" -> good: duplicate prevented.")
    else:
        print(" -> BAD: duplicate allowed!")
        
    print("\n4. testing login ok...")
    admin_auth = authenticate_user("admin_user", "adminpass")
    if admin_auth:
        print(f" -> admin login worked! data: {admin_auth}")
    else:
        print(" -> admin login failed.")
        
    analyst_auth = authenticate_user("analyst_electronics", "analystpass")
    if analyst_auth:
        print(f" -> analyst login worked! data: {analyst_auth}")
    else:
        print(" -> analyst login failed.")
        
    print("\n5. testing login fail (bad pass)...")
    bad_auth = authenticate_user("admin_user", "wrongpassword")
    if not bad_auth:
        print(" -> good: bad pass rejected.")
    else:
        print(" -> BAD: bad pass accepted!")
        
    print("\n6. testing role accessibility...")
    admin_cat = get_user_accessible_category(admin_auth)
    print(f" -> admin category limit: {admin_cat} (should be None)")
    
    analyst_cat = get_user_accessible_category(analyst_auth)
    print(f" -> analyst category limit: {analyst_cat} (should be 'Electronics')")

if __name__ == "__main__":
    test_auth()
