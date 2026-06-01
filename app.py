import streamlit as st
import pandas as pd
import os
from datetime import date
import re
from PIL import Image

st.set_page_config(page_title="Beat Plan Pro", page_icon="🚀", layout="wide")

# ====================== CREATE IMAGES FOLDER ======================
IMAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "store_images")
os.makedirs(IMAGE_DIR, exist_ok=True)

# ====================== STYLING ======================
st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #f0f4f8 0%, #e0e7ff 100%);}
    .main-header {
        font-size: 58px; font-weight: 800;
        background: linear-gradient(90deg, #1e3a8a, #6366f1, #a855f7);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center;
    }
    .store-card {
        background: white; padding: 15px; border-radius: 18px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1); text-align: center;
        transition: all 0.3s ease; height: 100%;
    }
    .store-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(99, 102, 241, 0.25);
    }
    .store-image {
        width: 100%; height: 160px; object-fit: cover;
        border-radius: 12px; margin-bottom: 12px;
    }
    .metric-card {
        background: white; padding: 24px; border-radius: 16px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08); text-align: center;
    }
    .stButton>button {border-radius: 12px; height: 52px; font-weight: 600;}
</style>
""", unsafe_allow_html=True)

# ====================== FILE PATHS ======================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMPLOYEE_FILE = os.path.join(BASE_DIR, "Employee_Master.xlsx")
GST_FILE = os.path.join(BASE_DIR, "GST_Master.xlsx")
PLANNED_FILE = os.path.join(BASE_DIR, "Planned_Visits.xlsx")
ADMIN_FILE = os.path.join(BASE_DIR, "Admin_Master.xlsx")

# Initialize Files
for file, cols in [
    (EMPLOYEE_FILE, ["EmployeeCode","EmployeeName","Password"]),
    (GST_FILE, ["StoreID","StoreName","GSTNumber","City","EmployeeCode"]),
    (PLANNED_FILE, ["EmployeeCode","EmployeeName","City","Store","GSTNumber","StoreID","VisitDate"]),
    (ADMIN_FILE, ["Username","Password"])
]:
    if not os.path.exists(file):
        pd.DataFrame(columns=cols).to_excel(file, index=False)

# Load Data
if "employee_df" not in st.session_state:
    st.session_state.employee_df = pd.read_excel(EMPLOYEE_FILE)
if "gst_df" not in st.session_state:
    st.session_state.gst_df = pd.read_excel(GST_FILE)
if "planned_df" not in st.session_state:
    st.session_state.planned_df = pd.read_excel(PLANNED_FILE)
if "admin_df" not in st.session_state:
    st.session_state.admin_df = pd.read_excel(ADMIN_FILE)

st.session_state.planned_df["VisitDate"] = pd.to_datetime(st.session_state.planned_df["VisitDate"], errors="coerce")

for k, v in {"logged_in": False, "role": "", "emp_code": "", "emp_name": ""}.items():
    if k not in st.session_state:
        st.session_state[k] = v

def is_valid_gstin(gstin):
    gstin = str(gstin).strip().upper()
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$'
    return bool(re.match(pattern, gstin))

def get_store_image_path(store_id):
    path = os.path.join(IMAGE_DIR, f"{store_id}.jpg")
    if os.path.exists(path):
        return path
    return None

def save_store_image(store_id, uploaded_file):
    image = Image.open(uploaded_file)
    image.save(os.path.join(IMAGE_DIR, f"{store_id}.jpg"))

# ====================== LOGIN ======================
if not st.session_state.logged_in:
    st.markdown("<h1 class='main-header'>🚀 Beat Plan Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:20px; color:#475569;'>Smart Store Visit Planning System</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        login_type = st.radio("Login Type", ["👨‍💼 Admin", "👷 Employee"], horizontal=True)

        if login_type == "👨‍💼 Admin":
            user = st.text_input("Username", placeholder="admin")
            pwd = st.text_input("Password", type="password")
            if st.button("Login as Admin", type="primary", use_container_width=True):
                if ((st.session_state.admin_df["Username"].astype(str) == user) & 
                    (st.session_state.admin_df["Password"].astype(str) == pwd)).any():
                    st.session_state.logged_in = True
                    st.session_state.role = "admin"
                    st.rerun()
                else:
                    st.error("❌ Invalid Credentials")
        else:
            emp_code = st.text_input("Employee Code", placeholder="EMP001")
            pwd = st.text_input("Password", type="password")
            if st.button("Login as Employee", type="primary", use_container_width=True):
                x = st.session_state.employee_df[
                    (st.session_state.employee_df["EmployeeCode"].astype(str) == emp_code) & 
                    (st.session_state.employee_df["Password"].astype(str) == pwd)
                ]
                if not x.empty:
                    st.session_state.logged_in = True
                    st.session_state.role = "employee"
                    st.session_state.emp_code = str(x.iloc[0]["EmployeeCode"])
                    st.session_state.emp_name = x.iloc[0]["EmployeeName"]
                    st.rerun()
                else:
                    st.error("❌ Invalid Credentials")
    st.stop()

if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.update({"logged_in": False, "role": "", "emp_code": "", "emp_name": ""})
    st.rerun()

# ====================== ADMIN PANEL ======================
if st.session_state.role == "admin":
    st.sidebar.title("🛠️ Admin Panel")
    menu = st.sidebar.radio("Menu", ["📊 Dashboard", "👥 Employees", "🏪 Stores", "📋 All Plans", "📸 Manage Store Photos"])

    if menu == "📊 Dashboard":
        st.title("📊 Admin Dashboard")
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="metric-card"><h2>{len(st.session_state.employee_df)}</h2><p>Employees</p></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card"><h2>{len(st.session_state.gst_df)}</h2><p>Stores</p></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card"><h2>{len(st.session_state.planned_df)}</h2><p>Total Plans</p></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="metric-card"><h2>{len(st.session_state.planned_df[st.session_state.planned_df["VisitDate"].dt.date == date.today()])}</h2><p>Today Visits</p></div>', unsafe_allow_html=True)

    elif menu == "👥 Employees":
        st.title("👥 All Employees")
        st.dataframe(st.session_state.employee_df, use_container_width=True, hide_index=True)

    elif menu == "🏪 Stores":
        st.title("🏪 All Stores")
        st.dataframe(st.session_state.gst_df, use_container_width=True, hide_index=True)

    elif menu == "📋 All Plans":
        st.title("📋 All Visit Plans")
        st.dataframe(st.session_state.planned_df.sort_values("VisitDate", ascending=False), use_container_width=True, hide_index=True)

    elif menu == "📸 Manage Store Photos":
        st.title("📸 Manage Store Photos")
        st.info("Upload or update photos for existing stores")

        # Search filter
        search = st.text_input("🔍 Search Store", placeholder="Store name or ID")
        df_display = st.session_state.gst_df.copy()

        if search:
            df_display = df_display[
                df_display["StoreName"].str.contains(search, case=False, na=False) |
                df_display["StoreID"].str.contains(search, case=False, na=False)
            ]

        for idx, row in df_display.iterrows():
            col1, col2, col3 = st.columns([1, 3, 2])
            with col1:
                img_path = get_store_image_path(row["StoreID"])
                if img_path:
                    st.image(img_path, width=120)
                else:
                    st.markdown("**No Photo**")

            with col2:
                st.write(f"**{row['StoreName']}**")
                st.caption(f"ID: {row['StoreID']} | GST: {row['GSTNumber']}")

            with col3:
                uploaded_file = st.file_uploader("Upload Photo", type=["jpg", "jpeg", "png"], 
                                               key=f"photo_{row['StoreID']}")
                if uploaded_file:
                    if st.button("💾 Save Photo", key=f"save_{row['StoreID']}"):
                        save_store_image(row["StoreID"], uploaded_file)
                        st.success(f"Photo updated for **{row['StoreName']}**!")
                        st.rerun()

# ====================== EMPLOYEE PANEL ======================
else:
    emp_code = st.session_state.emp_code
    emp_name = st.session_state.emp_name
    st.sidebar.title(f"👤 {emp_name}")

    menu = st.sidebar.radio("Menu", ["🎯 New Beat Plan", "📅 My Plans", "📆 Upcoming Plans", "➕ Add New Store"])

    employee_stores = st.session_state.gst_df[st.session_state.gst_df["EmployeeCode"].astype(str) == str(emp_code)]

    if menu == "🎯 New Beat Plan":
        # ... (Your existing code remains same)
        st.title("🎯 Create New Beat Plan")

        if employee_stores.empty:
            st.warning("No stores assigned yet.")
            st.stop()

        col1, col2 = st.columns([1,1])
        with col1:
            city = st.selectbox("📍 Select City", sorted(employee_stores["City"].dropna().unique()))
        with col2:
            visit_date = st.date_input("📅 Visit Date", value=date.today())

        city_stores = employee_stores[employee_stores["City"] == city].copy()

        planned_today = st.session_state.planned_df[
            (st.session_state.planned_df["EmployeeCode"].astype(str) == str(emp_code)) &
            (st.session_state.planned_df["VisitDate"].dt.date == visit_date)
        ]["StoreID"].tolist()

        available = city_stores[~city_stores["StoreID"].isin(planned_today)]

        st.subheader(f"🛍️ Available Stores in {city} ({len(available)})")

        if available.empty:
            st.success("✅ All stores planned for this date!")
        else:
            cols = st.columns(3)
            for idx, row in available.iterrows():
                img_path = get_store_image_path(row["StoreID"])
                
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="store-card">
                        {f'<img src="{img_path}" class="store-image">' if img_path else '<div style="height:160px; background:#f1f5f9; border-radius:12px; display:flex; align-items:center; justify-content:center; color:#64748b;">No Photo</div>'}
                        <h4>{row['StoreName']}</h4>
                        <p><b>ID:</b> {row['StoreID']}</p>
                        <small>{row['GSTNumber']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("✅ Plan This Visit", key=f"btn_{idx}"):
                        new_plan = pd.DataFrame([{
                            "EmployeeCode": emp_code,
                            "EmployeeName": emp_name,
                            "City": city,
                            "Store": row["StoreName"],
                            "StoreID": row["StoreID"],
                            "GSTNumber": row["GSTNumber"],
                            "VisitDate": pd.to_datetime(visit_date)
                        }])
                        st.session_state.planned_df = pd.concat([st.session_state.planned_df, new_plan], ignore_index=True)
                        st.session_state.planned_df.to_excel(PLANNED_FILE, index=False)
                        st.success(f"✅ Plan saved for **{row['StoreName']}**!")
                        st.rerun()

    elif menu == "📅 My Plans":
        st.title("📅 My Plans")
        my_plans = st.session_state.planned_df[st.session_state.planned_df["EmployeeCode"].astype(str) == str(emp_code)]
        st.dataframe(my_plans.sort_values("VisitDate", ascending=False) if not my_plans.empty else None, 
                    use_container_width=True, hide_index=True)

    elif menu == "📆 Upcoming Plans":
        st.title("📆 Upcoming Plans")
        upcoming = st.session_state.planned_df[
            (st.session_state.planned_df["EmployeeCode"].astype(str) == str(emp_code)) &
            (st.session_state.planned_df["VisitDate"].dt.date >= date.today())
        ].sort_values("VisitDate")
        st.dataframe(upcoming if not upcoming.empty else None, use_container_width=True, hide_index=True)

    elif menu == "➕ Add New Store":
        st.title("➕ Add New Store")
        with st.form("add_store"):
            col1, col2 = st.columns(2)
            with col1:
                gst_no = st.text_input("GST Number", max_chars=15).upper().strip()
                city = st.text_input("City").title().strip()
            with col2:
                store_name = st.text_input("Store Name").title().strip()
            
            store_photo = st.file_uploader("Upload Store Photo **(Mandatory)**", 
                                         type=["jpg", "jpeg", "png"], help="JPG, JPEG or PNG only")
            
            if st.form_submit_button("💾 Save Store", type="primary"):
                if not gst_no or not is_valid_gstin(gst_no):
                    st.error("❌ Invalid GST Number!")
                elif not city or not store_name:
                    st.error("❌ Store Name and City are required!")
                elif st.session_state.gst_df["GSTNumber"].astype(str).str.upper().eq(gst_no).any():
                    st.error("❌ GST Number already exists!")
                elif not store_photo:
                    st.error("❌ Store Photo is mandatory!")
                else:
                    next_id = f"S{len(st.session_state.gst_df)+1:05d}"
                    
                    new_store = pd.DataFrame([{
                        "StoreID": next_id,
                        "StoreName": store_name,
                        "GSTNumber": gst_no,
                        "City": city,
                        "EmployeeCode": emp_code
                    }])
                    
                    st.session_state.gst_df = pd.concat([st.session_state.gst_df, new_store], ignore_index=True)
                    st.session_state.gst_df.to_excel(GST_FILE, index=False)

                    # Save Photo (Mandatory)
                    save_store_image(next_id, store_photo)
                    st.success("✅ Store with Photo Added Successfully!")
                    st.rerun()