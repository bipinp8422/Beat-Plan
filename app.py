import streamlit as st
import pandas as pd
import os
import sqlite3
from datetime import date, timedelta
import re
import plotly.express as px
import io

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="Beat Plan Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== STYLING ======================
st.markdown("""
<style>
    .main-header {
        font-size: 48px; font-weight: 900;
        background: linear-gradient(90deg, #0066cc, #00a8e8, #00d4ff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin: 20px 0 10px 0;
    }
    .sub-header { text-align: center; color: #475569; font-size: 16px; margin-bottom: 30px; font-weight: 600; }
    .metric-card, .store-card, .progress-section {
        background: white; padding: 24px; border-radius: 16px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.08); border: 1px solid #e2e8f0;
    }
    .metric-value { font-size: 36px; font-weight: 800; color: #0066cc; }
</style>
""", unsafe_allow_html=True)

# ====================== FILE PATHS ======================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "beatplan.db")
EMPLOYEE_FILE = os.path.join(BASE_DIR, "Employee_Master.xlsx")
GST_FILE = os.path.join(BASE_DIR, "GST_Master.xlsx")
ADMIN_FILE = os.path.join(BASE_DIR, "Admin_Master.xlsx")

# ====================== DATABASE SETUP ======================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute('''CREATE TABLE IF NOT EXISTS planned_visits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    EmployeeCode TEXT,
                    EmployeeName TEXT,
                    City TEXT,
                    Store TEXT,
                    GSTNumber TEXT,
                    StoreID TEXT,
                    VisitDate DATE)''')
    conn.commit()
    conn.close()

def load_planned_df():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM planned_visits", conn)
    conn.close()
    if not df.empty:
        df["VisitDate"] = pd.to_datetime(df["VisitDate"]).dt.date
    else:
        df = pd.DataFrame(columns=["EmployeeCode", "EmployeeName", "City", "Store", "GSTNumber", "StoreID", "VisitDate"])
    return df

def save_planned_df(df):
    try:
        conn = sqlite3.connect(DB_FILE)
        df.to_sql('planned_visits', conn, if_exists='replace', index=False)
        conn.commit()
        conn.close()
        st.success("✅ Planned visits saved to database!")
        return True
    except Exception as e:
        st.error(f"❌ Save failed: {e}")
        return False

init_db()

# ====================== HELPER FUNCTIONS ======================
def load_or_create_df(file_path, columns):
    if os.path.exists(file_path) and os.path.getsize(file_path) > 100:
        try:
            return pd.read_excel(file_path)
        except:
            pass
    df = pd.DataFrame(columns=columns)
    df.to_excel(file_path, index=False)
    return df

def is_valid_gstin(gstin):
    gstin = str(gstin).strip().upper()
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$'
    return bool(re.match(pattern, gstin))

def get_progress_color(current, max_val):
    percent = (current / max_val) * 100
    if percent >= 100: return "#ef4444"
    elif percent >= 80: return "#f59e0b"
    else: return "#10b981"

# ====================== LOAD DATA ======================
if "employee_df" not in st.session_state:
    st.session_state.employee_df = load_or_create_df(EMPLOYEE_FILE, ["EmployeeCode", "EmployeeName", "Password"])
if "gst_df" not in st.session_state:
    st.session_state.gst_df = load_or_create_df(GST_FILE, ["StoreID", "StoreName", "GSTNumber", "City", "EmployeeCode"])
if "planned_df" not in st.session_state:
    st.session_state.planned_df = load_planned_df()
if "admin_df" not in st.session_state:
    st.session_state.admin_df = load_or_create_df(ADMIN_FILE, ["Username", "Password"])

# ====================== SESSION STATE ======================
for k, v in {"logged_in": False, "role": "", "emp_code": "", "emp_name": "", "selected_cities": []}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ====================== LOGIN ======================
if not st.session_state.logged_in:
    st.markdown("<h1 class='main-header'>🚀 Beat Plan Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Smart Store Visit Planning System</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        login_type = st.radio("Select Login Type", ["👨‍💼 Admin", "👷 Employee"], horizontal=True)

        if login_type == "👨‍💼 Admin":
            st.markdown("### Admin Login")
            user = st.text_input("Username", placeholder="Enter admin username")
            pwd = st.text_input("Password", type="password", placeholder="Enter password")
            if st.button("🔓 Login as Admin", type="primary", use_container_width=True):
                if ((st.session_state.admin_df["Username"].astype(str) == user) & 
                    (st.session_state.admin_df["Password"].astype(str) == pwd)).any():
                    st.session_state.logged_in = True
                    st.session_state.role = "admin"
                    st.success("✅ Admin login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials.")
        else:
            st.markdown("### Employee Login")
            emp_code = st.text_input("Employee Code", placeholder="e.g., EMP001")
            pwd = st.text_input("Password", type="password", placeholder="Enter password")
            if st.button("🔓 Login as Employee", type="primary", use_container_width=True):
                x = st.session_state.employee_df[
                    (st.session_state.employee_df["EmployeeCode"].astype(str) == emp_code) & 
                    (st.session_state.employee_df["Password"].astype(str) == pwd)
                ]
                if not x.empty:
                    st.session_state.logged_in = True
                    st.session_state.role = "employee"
                    st.session_state.emp_code = str(x.iloc[0]["EmployeeCode"])
                    st.session_state.emp_name = x.iloc[0]["EmployeeName"]
                    st.success(f"✅ Welcome, {st.session_state.emp_name}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials.")
    st.stop()

# ====================== LOGOUT ======================
col1, col2, col3 = st.columns([10, 1, 1])
with col3:
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.update({"logged_in": False, "role": "", "emp_code": "", "emp_name": "", "selected_cities": []})
        st.rerun()

# ====================== DOWNLOAD BUTTON ======================
def download_planned_button():
    if not st.session_state.planned_df.empty:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            st.session_state.planned_df.to_excel(writer, index=False)
        output.seek(0)
        st.download_button(
            "📥 Download Planned_Visits.xlsx", 
            output.getvalue(),
            f"Planned_Visits_{date.today()}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ====================== ADMIN PANEL ======================
if st.session_state.role == "admin":
    st.markdown("<h1 class='main-header'>🛠️ Admin Dashboard</h1>", unsafe_allow_html=True)
    
    admin_menu = st.sidebar.radio("Navigation", ["📊 Dashboard", "👥 Manage Employees", "🏪 Manage Stores", "📋 View Plans", "📤 Upload Masters"])

    if admin_menu == "📊 Dashboard":
        total_emp = len(st.session_state.employee_df)
        total_stores = len(st.session_state.gst_df)
        total_plans = len(st.session_state.planned_df)
        today_plans = len([d for d in st.session_state.planned_df["VisitDate"] if d == date.today()])

        col1, col2, col3, col4 = st.columns(4)
        for col, icon, label, value in zip([col1,col2,col3,col4], ["👥","🏪","📋","📅"], 
                                          ["Total Employees","Total Stores","Total Plans","Today's Visits"], 
                                          [total_emp, total_stores, total_plans, today_plans]):
            with col:
                st.markdown(f"""
                    <div class='metric-card'>
                        <div style='font-size:32px;'>{icon}</div>
                        <div>{label}</div>
                        <div class='metric-value'>{value}</div>
                    </div>
                """, unsafe_allow_html=True)
        download_planned_button()

    elif admin_menu == "👥 Manage Employees":
        tab1, tab2 = st.tabs(["View Employees", "Add New Employee"])
        with tab1: st.dataframe(st.session_state.employee_df, use_container_width=True, hide_index=True)
        with tab2:
            with st.form("add_employee"):
                col1, col2 = st.columns(2)
                with col1:
                    emp_code = st.text_input("Employee Code", placeholder="EMP001")
                    emp_name = st.text_input("Employee Name", placeholder="John Doe")
                with col2:
                    emp_pwd = st.text_input("Password", type="password")
                if st.form_submit_button("➕ Add Employee"):
                    if not emp_code or not emp_name or not emp_pwd:
                        st.error("All fields required!")
                    elif st.session_state.employee_df["EmployeeCode"].astype(str).str.upper().eq(emp_code.upper()).any():
                        st.error("Employee code already exists!")
                    else:
                        new_emp = pd.DataFrame([{"EmployeeCode": emp_code.upper(), "EmployeeName": emp_name.title(), "Password": emp_pwd}])
                        st.session_state.employee_df = pd.concat([st.session_state.employee_df, new_emp], ignore_index=True)
                        st.session_state.employee_df.to_excel(EMPLOYEE_FILE, index=False)
                        st.success("✅ Employee added!")
                        st.rerun()

    elif admin_menu == "🏪 Manage Stores":
        tab1, tab2 = st.tabs(["View Stores", "Add New Store"])
        with tab1: st.dataframe(st.session_state.gst_df, use_container_width=True, hide_index=True)
        with tab2:
            with st.form("add_store_admin"):
                col1, col2 = st.columns(2)
                with col1:
                    store_name = st.text_input("Store Name")
                    gst_no = st.text_input("GST Number", max_chars=15).upper().strip()
                with col2:
                    city = st.text_input("City")
                    emp_code_sel = st.selectbox("Assign Employee", st.session_state.employee_df["EmployeeCode"].unique() if not st.session_state.employee_df.empty else ["No Employees"])
                if st.form_submit_button("➕ Add Store"):
                    if not store_name or not gst_no or not city:
                        st.error("All fields required!")
                    elif not is_valid_gstin(gst_no):
                        st.error("Invalid GST Number!")
                    elif st.session_state.gst_df["GSTNumber"].astype(str).str.upper().eq(gst_no).any():
                        st.error("GST already exists!")
                    else:
                        next_id = f"S{len(st.session_state.gst_df)+1:05d}"
                        new_store = pd.DataFrame([{"StoreID": next_id, "StoreName": store_name.title(), "GSTNumber": gst_no, "City": city.title(), "EmployeeCode": emp_code_sel}])
                        st.session_state.gst_df = pd.concat([st.session_state.gst_df, new_store], ignore_index=True)
                        st.session_state.gst_df.to_excel(GST_FILE, index=False)
                        st.success("✅ Store added!")
                        st.rerun()

    elif admin_menu == "📋 View Plans":
        st.subheader("All Visit Plans")
        download_planned_button()
        # Filters and display (same logic as before)
        col1, col2, col3 = st.columns(3)
        with col1: filter_emp = st.selectbox("Filter by Employee", ["All"] + list(st.session_state.planned_df["EmployeeName"].dropna().unique()))
        with col2: filter_city = st.selectbox("Filter by City", ["All"] + list(st.session_state.planned_df["City"].dropna().unique()))
        with col3: date_range = st.date_input("Filter by Date", value=(date.today() - timedelta(days=30), date.today()))
        
        filtered = st.session_state.planned_df.copy()
        if filter_emp != "All": filtered = filtered[filtered["EmployeeName"] == filter_emp]
        if filter_city != "All": filtered = filtered[filtered["City"] == filter_city]
        if len(date_range) == 2:
            start, end = date_range
            filtered = filtered[(filtered["VisitDate"] >= start) & (filtered["VisitDate"] <= end)]
        st.dataframe(filtered.sort_values("VisitDate", ascending=False), use_container_width=True, hide_index=True)

    elif admin_menu == "📤 Upload Masters":
        # Upload sections for all masters...

# ====================== EMPLOYEE PANEL ======================
else:
    emp_code = st.session_state.emp_code
    emp_name = st.session_state.emp_name
    st.markdown(f"<h1 class='main-header'>👤 {emp_name}</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Your Beat Planning Dashboard</p>", unsafe_allow_html=True)

    employee_stores = st.session_state.gst_df[st.session_state.gst_df["EmployeeCode"].astype(str) == str(emp_code)]
    emp_menu = st.sidebar.radio("Navigation", ["🎯 New Beat Plan", "📅 My Plans", "📆 Upcoming Plans", "📊 Analytics", "➕ Request New Store"])

    if emp_menu == "🎯 New Beat Plan":
        # ... (same as your original with save_planned_df())
        if employee_stores.empty:
            st.warning("No stores assigned.")
            st.stop()

        col1, col2, col3 = st.columns(3)
        with col1: visit_date = st.date_input("Select Date", value=date.today())
        with col2: selected_cities = st.multiselect("Select Cities", sorted(employee_stores["City"].dropna().unique()), max_selections=3)
        with col3: 
            if st.button("Load Stores"): st.session_state.selected_cities = selected_cities

        daily_plans = st.session_state.planned_df[(st.session_state.planned_df["EmployeeCode"].astype(str) == str(emp_code)) & (st.session_state.planned_df["VisitDate"] == visit_date)]
        planned_count = len(daily_plans)

        # Progress bar
        progress_color = get_progress_color(planned_count, 10)
        st.markdown(f"<div class='progress-section'>Daily Progress: {planned_count}/10</div>", unsafe_allow_html=True)

        city_stores = employee_stores[employee_stores["City"].isin(st.session_state.selected_cities)] if st.session_state.selected_cities else employee_stores
        available = city_stores[~city_stores["StoreID"].isin(daily_plans["StoreID"].tolist())]

        for idx, row in available.iterrows():
            col1, col2 = st.columns([5,1])
            with col1:
                st.markdown(f"<div class='store-card'><strong>🏪 {row['StoreName']}</strong><br>City: {row['City']}<br>GST: {row['GSTNumber']}</div>", unsafe_allow_html=True)
            with col2:
                if st.button("➕ Add", key=f"add_{idx}"):
                    if planned_count < 10:
                        new_plan = pd.DataFrame([{
                            "EmployeeCode": emp_code, "EmployeeName": emp_name, "City": row["City"],
                            "Store": row["StoreName"], "StoreID": row["StoreID"], "GSTNumber": row["GSTNumber"],
                            "VisitDate": visit_date
                        }])
                        st.session_state.planned_df = pd.concat([st.session_state.planned_df, new_plan], ignore_index=True)
                        save_planned_df(st.session_state.planned_df)
                        st.rerun()

    download_planned_button()

st.caption("✅ Using SQLite Database • Data persists on Render")