import streamlit as st
import pandas as pd
import os
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
    * { margin: 0; padding: 0; }
    .stApp { background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); }
    .main-header {
        font-size: 48px; font-weight: 900;
        background: linear-gradient(90deg, #0066cc, #00a8e8, #00d4ff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin: 20px 0 10px 0; letter-spacing: -1px;
    }
    .sub-header { text-align: center; color: #475569; font-size: 16px; margin-bottom: 30px; font-weight: 600; }
    .metric-card, .store-card, .progress-section {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 24px; border-radius: 16px; border: 2px solid #e2e8f0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08); transition: all 0.3s ease;
    }
    .metric-card:hover, .store-card:hover {
        border-color: #0066cc; box-shadow: 0 8px 25px rgba(0, 102, 204, 0.15); transform: translateY(-2px);
    }
    .metric-value {
        font-size: 36px; font-weight: 800;
        background: linear-gradient(135deg, #0066cc, #00a8e8);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .stButton>button {
        border-radius: 12px; height: 48px; font-weight: 700;
        background: linear-gradient(90deg, #0066cc, #00a8e8) !important;
        color: white !important;
    }
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
    (EMPLOYEE_FILE, ["EmployeeCode", "EmployeeName", "Password"]),
    (GST_FILE, ["StoreID", "StoreName", "GSTNumber", "City", "EmployeeCode"]),
    (PLANNED_FILE, ["EmployeeCode", "EmployeeName", "City", "Store", "GSTNumber", "StoreID", "VisitDate"]),
    (ADMIN_FILE, ["Username", "Password"])
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

# Session State
for k, v in {"logged_in": False, "role": "", "emp_code": "", "emp_name": "", "selected_cities": []}.items():
    if k not in st.session_state:
        st.session_state[k] = v

def is_valid_gstin(gstin):
    gstin = str(gstin).strip().upper()
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$'
    return bool(re.match(pattern, gstin))

def get_progress_color(current, max_val):
    percent = (current / max_val) * 100
    if percent >= 100: return "#ef4444"
    elif percent >= 80: return "#f59e0b"
    else: return "#10b981"

# ====================== LOGIN ======================
if not st.session_state.logged_in:
    st.markdown("<h1 class='main-header'>🚀 Beat Plan Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Smart Store Visit Planning System</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        login_type = st.radio("Select Login Type", ["👨‍💼 Admin", "👷 Employee"], horizontal=True)

        if login_type == "👨‍💼 Admin":
            st.markdown("### Admin Login")
            user = st.text_input("Username", placeholder="Enter admin username", key="admin_user")
            pwd = st.text_input("Password", type="password", placeholder="Enter password", key="admin_pwd")
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
            emp_code = st.text_input("Employee Code", placeholder="e.g., EMP001", key="emp_code_login")
            pwd = st.text_input("Password", type="password", placeholder="Enter password", key="emp_pwd_login")
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

# ====================== ADMIN PANEL ======================
if st.session_state.role == "admin":
    st.markdown("<h1 class='main-header'>🛠️ Admin Dashboard</h1>", unsafe_allow_html=True)
    
    admin_menu = st.sidebar.radio(
        "Navigation",
        ["📊 Dashboard", "👥 Manage Employees", "🏪 Manage Stores", "📋 View Plans", "📤 Upload Masters", "⚙️ Settings"]
    )

    if admin_menu == "📊 Dashboard":
        total_emp = len(st.session_state.employee_df)
        total_stores = len(st.session_state.gst_df)
        total_plans = len(st.session_state.planned_df)
        today_plans = len(st.session_state.planned_df[st.session_state.planned_df["VisitDate"].dt.date == date.today()])

        col1, col2, col3, col4 = st.columns(4)
        for col, icon, label, value in zip([col1,col2,col3,col4], ["👥","🏪","📋","📅"], 
                                          ["Total Employees","Total Stores","Total Plans","Today's Visits"], 
                                          [total_emp, total_stores, total_plans, today_plans]):
            with col:
                st.markdown(f"""
                    <div class='metric-card'>
                        <div style='font-size:32px;'>{icon}</div>
                        <div class='metric-label'>{label}</div>
                        <div class='metric-value'>{value}</div>
                    </div>
                """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📈 Plans by Employee")
            st.bar_chart(st.session_state.planned_df.groupby("EmployeeName").size())
        with col2:
            st.subheader("🌍 Plans by City")
            plans_by_city = st.session_state.planned_df.groupby("City").size().reset_index(name="Plans")
            if not plans_by_city.empty:
                fig = px.pie(plans_by_city, names="City", values="Plans")
                st.plotly_chart(fig, use_container_width=True)

    elif admin_menu == "👥 Manage Employees":
        tab1, tab2 = st.tabs(["View Employees", "Add New Employee"])
        with tab1:
            st.dataframe(st.session_state.employee_df, use_container_width=True, hide_index=True)
        with tab2:
            with st.form("add_employee"):
                col1, col2 = st.columns(2)
                with col1:
                    emp_code = st.text_input("Employee Code", placeholder="EMP001")
                    emp_name = st.text_input("Employee Name", placeholder="John Doe")
                with col2:
                    emp_pwd = st.text_input("Password", type="password")
                if st.form_submit_button("➕ Add Employee", type="primary"):
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
        with tab1:
            st.dataframe(st.session_state.gst_df, use_container_width=True, hide_index=True)
        with tab2:
            with st.form("add_store_admin"):
                col1, col2 = st.columns(2)
                with col1:
                    store_name = st.text_input("Store Name")
                    gst_no = st.text_input("GST Number", max_chars=15).upper().strip()
                with col2:
                    city = st.text_input("City")
                    emp_code_sel = st.selectbox("Assign Employee", st.session_state.employee_df["EmployeeCode"].unique())
                if st.form_submit_button("➕ Add Store", type="primary"):
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

        col1, col2, col3 = st.columns(3)
        with col1:
            filter_emp = st.selectbox("Filter by Employee", ["All"] + list(st.session_state.planned_df["EmployeeName"].dropna().unique()))
        with col2:
            filter_city = st.selectbox("Filter by City", ["All"] + list(st.session_state.planned_df["City"].dropna().unique()))
        with col3:
            date_range = st.date_input("Filter by Date", value=(date.today() - timedelta(days=30), date.today()))

        filtered_plans = st.session_state.planned_df.copy()
        if filter_emp != "All":
            filtered_plans = filtered_plans[filtered_plans["EmployeeName"] == filter_emp]
        if filter_city != "All":
            filtered_plans = filtered_plans[filtered_plans["City"] == filter_city]
        if len(date_range) == 2:
            start, end = date_range
            filtered_plans = filtered_plans[(filtered_plans["VisitDate"].dt.date >= start) & (filtered_plans["VisitDate"].dt.date <= end)]

        # Export Buttons
        if not filtered_plans.empty:
            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                csv = filtered_plans.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Export CSV", csv, f"Beat_Plans_{date.today()}.csv", "text/csv")
            with col_exp2:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    filtered_plans.to_excel(writer, index=False, sheet_name="Visit_Plans")
                output.seek(0)
                st.download_button(
                    "📥 Export Excel",
                    output.getvalue(),
                    f"Beat_Plans_{date.today()}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        st.dataframe(filtered_plans.sort_values("VisitDate", ascending=False), use_container_width=True, hide_index=True)

    elif admin_menu == "📤 Upload Masters":
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("👥 Employee Master")
            uploaded = st.file_uploader("Upload Employee Excel", type="xlsx", key="emp_up")
            if uploaded and st.button("Upload Employees"):
                df = pd.read_excel(uploaded)
                df.to_excel(EMPLOYEE_FILE, index=False)
                st.session_state.employee_df = df
                st.success("Employee master updated!")
                st.rerun()
        with col2:
            st.subheader("🏪 Store Master")
            uploaded = st.file_uploader("Upload Store Excel", type="xlsx", key="store_up")
            if uploaded and st.button("Upload Stores"):
                df = pd.read_excel(uploaded)
                df.to_excel(GST_FILE, index=False)
                st.session_state.gst_df = df
                st.success("Store master updated!")
                st.rerun()

# ====================== EMPLOYEE PANEL ======================
else:
    emp_code = st.session_state.emp_code
    emp_name = st.session_state.emp_name
    st.markdown(f"<h1 class='main-header'>👤 {emp_name}</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Your Beat Planning Dashboard</p>", unsafe_allow_html=True)

    employee_stores = st.session_state.gst_df[st.session_state.gst_df["EmployeeCode"].astype(str) == str(emp_code)]

    emp_menu = st.sidebar.radio(
        "Navigation",
        ["🎯 New Beat Plan", "📅 My Plans", "📆 Upcoming Plans", "📊 Analytics", "➕ Request New Store"]
    )

    if emp_menu == "🎯 New Beat Plan":
        st.markdown("<p class='sub-header'>Create Your Daily Beat Plan</p>", unsafe_allow_html=True)

        if employee_stores.empty:
            st.warning("⚠️ No stores assigned. Contact Admin.")
            st.stop()

        col1, col2, col3 = st.columns(3)
        with col1:
            visit_date = st.date_input("📅 Select Date", value=date.today(), key="beat_date")
        with col2:
            selected_cities = st.multiselect("🌍 Select Cities", sorted(employee_stores["City"].dropna().unique()), max_selections=3)
        with col3:
            if st.button("🔍 Load Stores", use_container_width=True):
                st.session_state.selected_cities = selected_cities

        daily_plans = st.session_state.planned_df[
            (st.session_state.planned_df["EmployeeCode"].astype(str) == str(emp_code)) &
            (st.session_state.planned_df["VisitDate"].dt.date == visit_date)
        ]
        planned_count = len(daily_plans)

        progress_color = get_progress_color(planned_count, 10)
        st.markdown(f"""
            <div class='progress-section'>
                <div style='display:flex;justify-content:space-between;margin-bottom:8px;'>
                    <span>Daily Plan Progress</span>
                    <span style='font-weight:800;color:{progress_color};'>{planned_count}/10</span>
                </div>
                <div style='height:8px;background:#e2e8f0;border-radius:10px;'>
                    <div style='width:{min(planned_count*10,100)}%;height:100%;background:{progress_color};border-radius:10px;'></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if planned_count >= 10:
            st.error("🚫 Maximum 10 stores reached for today!")
        else:
            st.info(f"You can add {10 - planned_count} more stores today.")

        # Available Stores
        if st.session_state.selected_cities:
            city_stores = employee_stores[employee_stores["City"].isin(st.session_state.selected_cities)].copy()
        else:
            city_stores = employee_stores.copy()

        planned_ids = daily_plans["StoreID"].tolist()
        available = city_stores[~city_stores["StoreID"].isin(planned_ids)]

        st.markdown(f"### 🛍️ Available Stores ({len(available)})")
        if available.empty:
            st.info("No more stores available for selected cities.")
        else:
            for idx, row in available.iterrows():
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f"""
                        <div class='store-card'>
                            <div style='font-weight:700;font-size:18px;'>🏪 {row['StoreName']}</div>
                            <div style='margin-top:10px;'>
                                <strong>Store ID:</strong> {row['StoreID']}<br>
                                <strong>City:</strong> {row['City']}<br>
                                <strong>GST:</strong> {row['GSTNumber']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("➕ Add", key=f"add_{idx}"):
                        if planned_count < 10:
                            new_plan = pd.DataFrame([{
                                "EmployeeCode": emp_code,
                                "EmployeeName": emp_name,
                                "City": row["City"],
                                "Store": row["StoreName"],
                                "StoreID": row["StoreID"],
                                "GSTNumber": row["GSTNumber"],
                                "VisitDate": pd.to_datetime(visit_date)
                            }])
                            st.session_state.planned_df = pd.concat([st.session_state.planned_df, new_plan], ignore_index=True)
                            st.session_state.planned_df.to_excel(PLANNED_FILE, index=False)
                            st.success(f"✅ {row['StoreName']} added to plan!")
                            st.rerun()

    elif emp_menu == "📅 My Plans":
        my_plans = st.session_state.planned_df[st.session_state.planned_df["EmployeeCode"].astype(str) == str(emp_code)]
        if my_plans.empty:
            st.info("No plans yet. Create one from New Beat Plan.")
        else:
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("Total Plans", len(my_plans))
            with col2: st.metric("Cities", my_plans['City'].nunique())
            with col3: st.metric("Dates", my_plans['VisitDate'].dt.date.nunique())
            st.dataframe(my_plans.sort_values("VisitDate", ascending=False), use_container_width=True, hide_index=True)

    elif emp_menu == "📆 Upcoming Plans":
        upcoming = st.session_state.planned_df[
            (st.session_state.planned_df["EmployeeCode"].astype(str) == str(emp_code)) &
            (st.session_state.planned_df["VisitDate"].dt.date >= date.today())
        ].sort_values("VisitDate")
        if upcoming.empty:
            st.info("No upcoming visits.")
        else:
            for vdate in upcoming["VisitDate"].dt.date.unique():
                plans = upcoming[upcoming["VisitDate"].dt.date == vdate]
                st.markdown(f"**📅 {vdate.strftime('%A, %d %B %Y')}** ({len(plans)} stores)")
                for _, p in plans.iterrows():
                    st.markdown(f"• **{p['Store']}** - {p['City']}")

    elif emp_menu == "📊 Analytics":
        my_plans = st.session_state.planned_df[st.session_state.planned_df["EmployeeCode"].astype(str) == str(emp_code)]
        if my_plans.empty:
            st.info("No data yet.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.bar_chart(my_plans.groupby("City").size().rename("Stores"))
            with col2:
                my_plans["Month"] = my_plans["VisitDate"].dt.to_period("M").astype(str)
                st.line_chart(my_plans.groupby("Month").size().rename("Visits"))

    elif emp_menu == "➕ Request New Store":
        st.subheader("Request New Store")
        with st.form("store_request"):
            col1, col2 = st.columns(2)
            with col1:
                sname = st.text_input("Store Name")
                city = st.text_input("City")
            with col2:
                gst = st.text_input("GST Number", max_chars=15).upper().strip()
                reason = st.text_area("Reason", height=100)
            if st.form_submit_button("Submit Request"):
                if sname and city and gst and reason and is_valid_gstin(gst):
                    st.success("✅ Request sent to Admin!")
                else:
                    st.error("Please fill all fields correctly.")

st.caption("Beat Plan Pro © 2026")