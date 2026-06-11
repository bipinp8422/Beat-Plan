#!/usr/bin/env python3
"""
Setup script to populate Supabase with initial test data
Run this ONCE after creating your Supabase project
"""

from supabase import create_client, Client
import os
import sys

# You'll need to set these as environment variables or enter them when prompted
SUPABASE_URL = os.getenv("SUPABASE_URL") or input("Enter your SUPABASE_URL: ")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or input("Enter your SUPABASE_KEY: ")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: Supabase credentials required!")
    sys.exit(1)

print(f"\n🔗 Connecting to Supabase: {SUPABASE_URL}")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    # Test connection
    supabase.table("admin_master").select("*").limit(1).execute()
    print("✅ Connection successful!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("⚠️  Make sure:")
    print("   1. Tables are created (run SQL from guide)")
    print("   2. URL format is correct (no trailing slash)")
    print("   3. API Key is correct (Anon Key, not Service Role)")
    sys.exit(1)

# ====================== DATA TO INSERT ======================

admin_data = [
    {"Username": "admin", "Password": "admin123"},
    {"Username": "manager", "Password": "manager123"},
]

employee_data = [
    {"EmployeeCode": "EMP001", "EmployeeName": "John Doe", "Password": "john123"},
    {"EmployeeCode": "EMP002", "EmployeeName": "Jane Smith", "Password": "jane123"},
    {"EmployeeCode": "EMP003", "EmployeeName": "Mike Johnson", "Password": "mike123"},
]

store_data = [
    {
        "StoreID": "S00001",
        "StoreName": "Store A - Mumbai",
        "GSTNumber": "27AABCS1234D2Z5",
        "City": "Mumbai",
        "EmployeeCode": "EMP001",
    },
    {
        "StoreID": "S00002",
        "StoreName": "Store B - Mumbai",
        "GSTNumber": "27AABCS1234D2Z6",
        "City": "Mumbai",
        "EmployeeCode": "EMP001",
    },
    {
        "StoreID": "S00003",
        "StoreName": "Store C - Delhi",
        "GSTNumber": "27AABCS1234D2Z7",
        "City": "Delhi",
        "EmployeeCode": "EMP002",
    },
    {
        "StoreID": "S00004",
        "StoreName": "Store D - Delhi",
        "GSTNumber": "27AABCS1234D2Z8",
        "City": "Delhi",
        "EmployeeCode": "EMP002",
    },
    {
        "StoreID": "S00005",
        "StoreName": "Store E - Bangalore",
        "GSTNumber": "27AABCS1234D2Z9",
        "City": "Bangalore",
        "EmployeeCode": "EMP003",
    },
    {
        "StoreID": "S00006",
        "StoreName": "Store F - Pune",
        "GSTNumber": "27AABCS1234E2Z0",
        "City": "Pune",
        "EmployeeCode": "EMP003",
    },
]

# ====================== INSERT DATA ======================

print("\n" + "="*60)
print("📊 POPULATING SUPABASE WITH TEST DATA")
print("="*60)

# Insert Admins
print("\n👨‍💼 Adding Admin Credentials...")
try:
    supabase.table("admin_master").delete().neq("id", -1).execute()
    supabase.table("admin_master").insert(admin_data).execute()
    print(f"✅ Added {len(admin_data)} admin accounts")
    for admin in admin_data:
        print(f"   • {admin['Username']} / {admin['Password']}")
except Exception as e:
    print(f"❌ Error adding admins: {e}")

# Insert Employees
print("\n👷 Adding Test Employees...")
try:
    supabase.table("employee_master").delete().neq("id", -1).execute()
    supabase.table("employee_master").insert(employee_data).execute()
    print(f"✅ Added {len(employee_data)} employees")
    for emp in employee_data:
        print(f"   • {emp['EmployeeCode']}: {emp['EmployeeName']} / {emp['Password']}")
except Exception as e:
    print(f"❌ Error adding employees: {e}")

# Insert Stores
print("\n🏪 Adding Test Stores...")
try:
    supabase.table("gst_master").delete().neq("id", -1).execute()
    supabase.table("gst_master").insert(store_data).execute()
    print(f"✅ Added {len(store_data)} stores")
    for store in store_data:
        print(f"   • {store['StoreName']} ({store['City']})")
except Exception as e:
    print(f"❌ Error adding stores: {e}")

# ====================== VERIFY DATA ======================

print("\n" + "="*60)
print("✅ VERIFICATION")
print("="*60)

try:
    admins = supabase.table("admin_master").select("*").execute()
    print(f"\n✅ Admin Accounts: {len(admins.data)}")
    
    employees = supabase.table("employee_master").select("*").execute()
    print(f"✅ Employees: {len(employees.data)}")
    
    stores = supabase.table("gst_master").select("*").execute()
    print(f"✅ Stores: {len(stores.data)}")
    
except Exception as e:
    print(f"❌ Verification failed: {e}")

print("\n" + "="*60)
print("🎉 SETUP COMPLETE!")
print("="*60)
print("\n📝 You can now login with:")
print("   Admin: username='admin', password='admin123'")
print("   Employee: code='EMP001', password='john123'")
print("\n🚀 Run your Streamlit app:")
print("   streamlit run app_supabase.py")
print("\n" + "="*60)
