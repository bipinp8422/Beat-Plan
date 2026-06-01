import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta
import plotly.express as px
import re
def is_valid_gstin(gstin):
    gstin = str(gstin).strip().upper()
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$'
    return bool(re.match(pattern, gstin))

st.set_page_config(page_title="Beat Plan Pro", page_icon="🚀", layout="wide")

# ====================== STYLING ======================
st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%);}
    .main-header {font-size: 48px; font-weight: bold; background: linear-gradient(90deg, #1e40af, #6d28d9); 
                  -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center;}
    .metric-card {
        background: white; padding: 25px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        text-align: center; border: 1px solid #e2e8f0;
    }
    .metric-value {font-size: 42px; font-weight: bold; color: #1e40af;}
    .metric-label {font-size: 16px; color: #64748b; margin-top: 8px;}
</style>
""", unsafe_allow_html=True)

# ====================== FILE PATHS ======================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMPLOYEE_FILE = os.path.join(BASE_DIR, "Employee_Master.xlsx")
GST_FILE = os.path.join(BASE_DIR, "GST_Master.xlsx")
PLANNED_FILE = os.path.join(BASE_DIR, "Planned_Visits.xlsx")
ADMIN_FILE = os.path.join(BASE_DIR, "Admin_Master.xlsx")

# Initialize Files if not exist
for file, cols in [
    (EMPLOYEE_FILE, ["EmployeeCode","EmployeeName","Password"]),
    (GST_FILE, ["StoreID","StoreName","GSTNumber","City","EmployeeCode"]),
    (PLANNED_FILE, ["EmployeeCode","EmployeeName","City","Store","GSTNumber","StoreID","VisitDate"]),
    (ADMIN_FILE, ["Username","Password"])
]:
    if not os.path.exists(file):
        pd.DataFrame(columns=cols).to_excel(file, index=False)

# Load Data into Session State (Best Practice)
if "employee_df" not in st.session_state:
    st.session_state.employee_df = pd.read_excel(EMPLOYEE_FILE)
if "gst_df" not in st.session_state:
    st.session_state.gst_df = pd.read_excel(GST_FILE)
if "planned_df" not in st.session_state:
    st.session_state.planned_df = pd.read_excel(PLANNED_FILE)
if "admin_df" not in st.session_state:
    st.session_state.admin_df = pd.read_excel(ADMIN_FILE)

st.session_state.planned_df["VisitDate"] = pd.to_datetime(st.session_state.planned_df["VisitDate"], errors="coerce")

# Session State for Login
for k, v in {"logged_in":False, "role":"", "emp_code":"", "emp_name":""}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ====================== LOGIN ======================
if not st.session_state.logged_in:
    st.markdown("<h1 class='main-header'>🚀 Beat Plan Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:18px; color:#475569;'>Smart Store Visit Planning System</p>", unsafe_allow_html=True)

    login_type = st.radio("Login Type", ["Admin", "Employee"], horizontal=True)

    if login_type == "Admin":
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Admin Login", use_container_width=True):
            if ((st.session_state.admin_df["Username"].astype(str) == user) & 
                (st.session_state.admin_df["Password"].astype(str) == pwd)).any():
                st.session_state.logged_in = True
                st.session_state.role = "admin"
                st.rerun()
    else:
        emp_code = st.text_input("Employee Code")
        pwd = st.text_input("Password", type="password")
        if st.button("Employee Login", use_container_width=True):
            x = st.session_state.employee_df[
                (st.session_state.employee_df["EmployeeCode"].astype(str)==emp_code) & 
                (st.session_state.employee_df["Password"].astype(str)==pwd)
            ]
            if not x.empty:
                st.session_state.logged_in = True
                st.session_state.role = "employee"
                st.session_state.emp_code = x.iloc[0]["EmployeeCode"]
                st.session_state.emp_name = x.iloc[0]["EmployeeName"]
                st.rerun()
    st.stop()

if st.sidebar.button("🚪 Logout"):
    st.session_state.update({"logged_in":False, "role":"", "emp_code":"", "emp_name":""})
    st.rerun()

# ====================== ADMIN PANEL ======================
if st.session_state.role == "admin":
    st.sidebar.title("🛠️ Admin Panel")
    menu = st.sidebar.radio("Menu", ["Dashboard", "Employees", "Stores", "All Plans", "Upload Masters"])

    if menu == "Dashboard":
        st.title("📊 Admin Dashboard")
        df_planned = st.session_state.planned_df
        df_emp = st.session_state.employee_df
        df_gst = st.session_state.gst_df

        total_plans = len(df_planned)
        total_emp = len(df_emp)
        total_stores = len(df_gst)
        today_plans = len(df_planned[df_planned["VisitDate"].dt.date == date.today()])

        col1, col2, col3, col4 = st.columns(4)
        with col1: st.markdown(f'<div class="metric-card"><div class="metric-value">{total_emp}</div><div class="metric-label">👥 Employees</div></div>', unsafe_allow_html=True)
        with col2: st.markdown(f'<div class="metric-card"><div class="metric-value">{total_stores}</div><div class="metric-label">🏪 Stores</div></div>', unsafe_allow_html=True)
        with col3: st.markdown(f'<div class="metric-card"><div class="metric-value">{total_plans}</div><div class="metric-label">📅 Total Plans</div></div>', unsafe_allow_html=True)
        with col4: st.markdown(f'<div class="metric-card"><div class="metric-value">{today_plans}</div><div class="metric-label">📍 Today Plans</div></div>', unsafe_allow_html=True)

    elif menu == "Employees":
        st.title("👥 All Employees")
        st.dataframe(st.session_state.employee_df, use_container_width=True)

    elif menu == "Stores":
        st.title("🏪 All Stores")
        st.dataframe(st.session_state.gst_df, use_container_width=True)

    elif menu == "All Plans":
        st.title("📋 All Visit Plans")
        st.dataframe(st.session_state.planned_df.sort_values("VisitDate", ascending=False), use_container_width=True)

        with open(PLANNED_FILE, "rb") as f:
            st.download_button("📥 Download All Plans", f, "All_Plans.xlsx", use_container_width=True)

    elif menu == "Upload Masters":
        st.title("📤 Upload Master Files")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Employee Master")
            uploaded_emp = st.file_uploader("Upload Employee Master", type=["xlsx"], key="emp")
            if uploaded_emp:
                new_df = pd.read_excel(uploaded_emp)
                new_df.to_excel(EMPLOYEE_FILE, index=False)
                st.session_state.employee_df = new_df
                st.success("✅ Employee Master Updated!")
        with col2:
            st.subheader("Store Master")
            uploaded_gst = st.file_uploader("Upload Store Master", type=["xlsx"], key="gst")
            if uploaded_gst:
                new_df = pd.read_excel(uploaded_gst)
                new_df.to_excel(GST_FILE, index=False)
                st.session_state.gst_df = new_df
                st.success("✅ Store Master Updated!")

# ====================== EMPLOYEE PANEL ======================
else:
    emp_code = st.session_state.emp_code
    emp_name = st.session_state.emp_name

    st.sidebar.title(f"👤 {emp_name}")
    menu = st.sidebar.radio("Menu", ["Beat Plan", "My Plans", "Upcoming Plans", "Add New Store"])

    employee_stores = st.session_state.gst_df[st.session_state.gst_df["EmployeeCode"].astype(str) == str(emp_code)]

    if menu == "Beat Plan":
        st.title("🎯 Create New Beat Plan")

        if employee_stores.empty:
            st.warning("No stores assigned yet.")
            st.stop()

        city = st.selectbox("Select City", sorted(employee_stores["City"].dropna().unique()))
        visit_date = st.date_input("Visit Date", value=date.today())

        city_stores = employee_stores[employee_stores["City"] == city].copy()
        city_stores["Display"] = city_stores["StoreName"] + " (" + city_stores["StoreID"] + ")"

        planned_today = st.session_state.planned_df[
            (st.session_state.planned_df["EmployeeCode"].astype(str) == str(emp_code)) &
            (st.session_state.planned_df["VisitDate"].dt.date == visit_date)
        ]["StoreID"].astype(str).tolist()

        available_stores = city_stores[~city_stores["StoreID"].astype(str).isin(planned_today)]

        st.subheader("📌 Pending Stores")
        if available_stores.empty:
            st.success("✅ All stores already planned for this date.")
        else:
            st.dataframe(
    available_stores[["StoreID", "StoreName", "City", "GSTNumber"]],
    hide_index=True,
    use_container_width=True
)
            selected_store = st.selectbox("Select Store", available_stores["Display"])

            if st.button("✅ Save Visit Plan", type="primary", use_container_width=True):
                row = available_stores[available_stores["Display"] == selected_store].iloc[0]

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

    elif menu == "My Plans":
        st.title("📅 My Plans")
        my_plans = st.session_state.planned_df[st.session_state.planned_df["EmployeeCode"].astype(str) == str(emp_code)]
        if my_plans.empty:
            st.info("No plans created yet.")
        else:
            st.dataframe(my_plans.sort_values("VisitDate", ascending=False), use_container_width=True)

    elif menu == "Upcoming Plans":
        st.title("📆 Upcoming Plans")
        upcoming = st.session_state.planned_df[
            (st.session_state.planned_df["EmployeeCode"].astype(str) == str(emp_code)) &
            (st.session_state.planned_df["VisitDate"].dt.date >= date.today())
        ].sort_values("VisitDate")

        if not upcoming.empty:
            st.dataframe(upcoming, use_container_width=True)
        else:
            st.info("No upcoming plans.")

    elif menu == "Add New Store":
        st.title("➕ Add New Store")

    gst_no = st.text_input(
        "GST Number",
        max_chars=15,
        help="Enter valid 15-digit GSTIN"
    ).upper().strip()

    city = st.text_input("City").upper().strip()
    store_name = st.text_input("Store Name").upper().strip()

    if st.button("Save Store", use_container_width=True):

        if not gst_no:
            st.error("Please enter GST Number")

        elif not is_valid_gstin(gst_no):
            st.error("❌ Invalid GST Number Format! Example: 27ABCDE1234F1Z5")

        elif not city:
            st.error("Please enter City")

        elif not store_name:
            st.error("Please enter Store Name")

        elif st.session_state.gst_df["GSTNumber"].astype(str).str.upper().eq(gst_no).any():
            st.error("GST Number already exists!")

        else:
            next_id = f"S{len(st.session_state.gst_df)+1:05d}"

            new_store = pd.DataFrame([{
                "StoreID": next_id,
                "StoreName": store_name,
                "GSTNumber": gst_no,
                "City": city,
                "EmployeeCode": emp_code
            }])

            st.session_state.gst_df = pd.concat(
                [st.session_state.gst_df, new_store],
                ignore_index=True
            )

            st.session_state.gst_df.to_excel(GST_FILE, index=False)

            st.success("✅ Store Added Successfully!")
            st.rerun()