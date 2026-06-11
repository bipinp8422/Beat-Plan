import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta
import re
import io
from supabase import create_client, Client

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="Beat Plan Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== SUPABASE CONFIG ======================
SUPABASE_URL = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("❌ Missing Supabase credentials!")
    st.info("📝 Add these to `.streamlit/secrets.toml`:\n```toml\nSUPABASE_URL = 'your_url'\nSUPABASE_KEY = 'your_key'\n```")
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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

# ====================== DATABASE FUNCTIONS ======================
def init_db():
    try:
        supabase.table("planned_visits").select("*").limit(1).execute()
        return True
    except Exception as e:
        st.error(f"❌ Supabase connection failed: {e}")
        return False

def clean_dataframe(df):
    if df.empty:
        return df
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
    if "VisitDate" in df.columns:
        df["VisitDate"] = pd.to_datetime(df["VisitDate"], errors='coerce').dt.date
    return df

def load_from_supabase(table_name, columns):
    try:
        response = supabase.table(table_name).select("*").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            return clean_dataframe(df)
        return pd.DataFrame(columns=columns)
    except Exception as e:
        st.warning(f"Error loading {table_name}: {e}")
        return pd.DataFrame(columns=columns)

def save_to_supabase(table_name, df):
    try:
        df_copy = df.copy()
        if 'id' in df_copy.columns:
            df_copy = df_copy.drop('id', axis=1)
        
        for col in df_copy.columns:
            if pd.api.types.is_datetime64_any_dtype(df_copy[col]) or col in ['VisitDate']:
                df_copy[col] = pd.to_datetime(df_copy[col]).astype(str)
        
        try:
            supabase.table(table_name).delete().neq("id", -1).execute()
        except:
            pass
        
        if not df_copy.empty:
            records = df_copy.to_dict('records')
            supabase.table(table_name).insert(records).execute()
        return True
    except Exception as e:
        st.error(f"Save failed: {e}")
        return False

# ====================== INITIALIZE ======================
if not init_db():
    st.stop()

if "employee_df" not in st.session_state:
    st.session_state.employee_df = load_from_supabase("employee_master", ["EmployeeCode", "EmployeeName", "Password"])
if "gst_df" not in st.session_state:
    st.session_state.gst_df = load_from_supabase("gst_master", ["StoreID", "StoreName", "GSTNumber", "City", "EmployeeCode"])
if "planned_df" not in st.session_state:
    st.session_state.planned_df = load_from_supabase("planned_visits", ["EmployeeCode", "EmployeeName", "City", "Store", "GSTNumber", "StoreID", "VisitDate"])
if "admin_df" not in st.session_state:
    st.session_state.admin_df = load_from_supabase("admin_master", ["Username", "Password"])

# ====================== SESSION STATE ======================
default_state = {"logged_in": False, "role": "", "emp_code": "", "emp_name": "", "selected_cities": []}
for k, v in default_state.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ====================== HELPERS ======================
def is_valid_gstin(gstin):
    gstin = str(gstin).strip().upper()
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$'
    return bool(re.match(pattern, gstin))

def get_progress_color(current, max_val):
    percent = (current / max_val) * 100
    if percent >= 100: return "#ef4444"
    elif percent >= 80: return "#f59e0b"
    return "#10b981"

def download_beat_plan_button(df, key, filename_prefix="Beat_Plan"):
    if not df.empty:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Beat Plan')
        output.seek(0)
        st.download_button(
            label="📥 Download Beat Plan (Excel)",
            data=output.getvalue(),
            file_name=f"{filename_prefix}_{date.today().strftime('%Y-%m-%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key=key
        )

# ====================== LOGIN PAGE ======================
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
                if not user or not pwd:
                    st.error("❌ Please enter both username and password.")
                else:
                    df = st.session_state.admin_df.copy()
                    df["Username"] = df["Username"].astype(str).str.strip()
                    df["Password"] = df["Password"].astype(str).str.strip()
                    if ((df["Username"] == user.strip()) & (df["Password"] == pwd.strip())).any():
                        st.session_state.logged_in = True
                        st.session_state.role = "admin"
                        st.success("✅ Admin login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials.")
        else:
            st.markdown("### Employee Login")
            emp_code_input = st.text_input("Employee Code", placeholder="e.g., D77809", key="emp_code_login")
            pwd_input = st.text_input("Password", type="password", placeholder="Enter password", key="emp_pwd_login")
            
            if st.button("🔓 Login as Employee", type="primary", use_container_width=True):
                if not emp_code_input or not pwd_input:
                    st.error("❌ Please enter both Employee Code and Password.")
                else:
                    emp_code_clean = str(emp_code_input).strip()
                    pwd_clean = str(pwd_input).strip()
                    
                    df = st.session_state.employee_df.copy()
                    df["EmployeeCode"] = df["EmployeeCode"].astype(str).str.strip()
                    df["Password"] = df["Password"].astype(str).str.strip()
                    
                    x = df[(df["EmployeeCode"] == emp_code_clean) & (df["Password"] == pwd_clean)]
                    
                    if not x.empty:
                        st.session_state.logged_in = True
                        st.session_state.role = "employee"
                        st.session_state.emp_code = str(x.iloc[0]["EmployeeCode"])
                        st.session_state.emp_name = x.iloc[0]["EmployeeName"]
                        st.success(f"✅ Welcome, {st.session_state.emp_name}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials. Please check Employee Code and Password.")
    st.stop()

# ====================== LOGOUT ======================
col1, col2, col3 = st.columns([10, 1, 1])
with col3:
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.role = ""
        st.session_state.emp_code = ""
        st.session_state.emp_name = ""
        st.session_state.selected_cities = []
        st.rerun()

# ====================== ADMIN PANEL ======================
if st.session_state.role == "admin":
    st.markdown("<h1 class='main-header'>🛠️ Admin Dashboard</h1>", unsafe_allow_html=True)
    
    admin_menu = st.sidebar.radio(
        "Navigation", ["📊 Dashboard", "👥 Manage Employees", "🏪 Manage Stores", "📋 View Plans", "🔄 Refresh Data"]
    )
    
    if admin_menu == "📊 Dashboard":
        total_emp = len(st.session_state.employee_df)
        total_stores = len(st.session_state.gst_df)
        total_plans = len(st.session_state.planned_df)
        today_plans = sum(1 for d in st.session_state.planned_df.get("VisitDate", []) if d == date.today())
        
        cols = st.columns(4)
        metrics = [
            ("👥", "Total Employees", total_emp),
            ("🏪", "Total Stores", total_stores),
            ("📋", "Total Plans", total_plans),
            ("📅", "Today's Visits", today_plans)
        ]
        for col, (icon, label, value) in zip(cols, metrics):
            with col:
                st.markdown(f"""
                    <div class='metric-card'>
                        <div style='font-size:32px;'>{icon}</div>
                        <div>{label}</div>
                        <div class='metric-value'>{value}</div>
                    </div>
                """, unsafe_allow_html=True)

    elif admin_menu == "👥 Manage Employees":
        tab1, tab2 = st.tabs(["View Employees", "Add New Employee"])
        with tab1:
            st.dataframe(st.session_state.employee_df, use_container_width=True, hide_index=True) if not st.session_state.employee_df.empty else st.info("No employees yet.")
        with tab2:
            with st.form("add_employee"):
                c1, c2 = st.columns(2)
                with c1:
                    ecode = st.text_input("Employee Code")
                    ename = st.text_input("Employee Name")
                with c2:
                    epwd = st.text_input("Password", type="password")
                if st.form_submit_button("➕ Add Employee", type="primary"):
                    if not ecode or not ename or not epwd:
                        st.error("All fields required!")
                    elif st.session_state.employee_df["EmployeeCode"].astype(str).str.upper().eq(ecode.strip().upper()).any():
                        st.error("Employee code already exists!")
                    else:
                        new_row = pd.DataFrame([{"EmployeeCode": ecode.strip().upper(), "EmployeeName": ename.strip().title(), "Password": epwd.strip()}])
                        st.session_state.employee_df = pd.concat([st.session_state.employee_df, new_row], ignore_index=True)
                        if save_to_supabase("employee_master", st.session_state.employee_df):
                            st.success("✅ Employee added!")
                            st.rerun()

    elif admin_menu == "🏪 Manage Stores":
        tab1, tab2 = st.tabs(["View Stores", "Add New Store"])
        with tab1:
            st.dataframe(st.session_state.gst_df, use_container_width=True, hide_index=True) if not st.session_state.gst_df.empty else st.info("No stores yet.")
        with tab2:
            with st.form("add_store_admin"):
                c1, c2 = st.columns(2)
                with c1:
                    sname = st.text_input("Store Name")
                    gstno = st.text_input("GST Number", max_chars=15).upper().strip()
                with c2:
                    city = st.text_input("City")
                    emp_sel = st.selectbox("Assign Employee", st.session_state.employee_df["EmployeeCode"].unique() if not st.session_state.employee_df.empty else ["No Employees"])
                if st.form_submit_button("➕ Add Store", type="primary"):
                    if not sname or not gstno or not city:
                        st.error("All fields required!")
                    elif not is_valid_gstin(gstno):
                        st.error("Invalid GST Number!")
                    elif st.session_state.gst_df["GSTNumber"].astype(str).str.upper().eq(gstno).any():
                        st.error("GST already exists!")
                    else:
                        next_id = f"S{len(st.session_state.gst_df)+1:05d}"
                        new_store = pd.DataFrame([{"StoreID": next_id, "StoreName": sname.strip().title(), "GSTNumber": gstno, "City": city.strip().title(), "EmployeeCode": emp_sel}])
                        st.session_state.gst_df = pd.concat([st.session_state.gst_df, new_store], ignore_index=True)
                        if save_to_supabase("gst_master", st.session_state.gst_df):
                            st.success("✅ Store added!")
                            st.rerun()

    elif admin_menu == "📋 View Plans":
        st.subheader("All Visit Plans")
        c1, c2, c3 = st.columns(3)
        with c1: femp = st.selectbox("Filter by Employee", ["All"] + list(st.session_state.planned_df["EmployeeName"].dropna().unique()))
        with c2: fcity = st.selectbox("Filter by City", ["All"] + list(st.session_state.planned_df["City"].dropna().unique()))
        with c3: drange = st.date_input("Filter by Date", value=(date.today() - timedelta(days=30), date.today()))
        
        fp = st.session_state.planned_df.copy()
        if femp != "All": fp = fp[fp["EmployeeName"] == femp]
        if fcity != "All": fp = fp[fp["City"] == fcity]
        if len(drange) == 2:
            fp = fp[(fp["VisitDate"] >= drange[0]) & (fp["VisitDate"] <= drange[1])]
        
        st.dataframe(fp.sort_values("VisitDate", ascending=False), use_container_width=True, hide_index=True)
        download_beat_plan_button(fp.sort_values("VisitDate", ascending=False), "admin_download", "Beat_Plan_Admin")

    elif admin_menu == "🔄 Refresh Data":
        if st.button("🔄 Refresh All Data", type="primary", use_container_width=True):
            st.session_state.employee_df = load_from_supabase("employee_master", ["EmployeeCode", "EmployeeName", "Password"])
            st.session_state.gst_df = load_from_supabase("gst_master", ["StoreID", "StoreName", "GSTNumber", "City", "EmployeeCode"])
            st.session_state.planned_df = load_from_supabase("planned_visits", ["EmployeeCode", "EmployeeName", "City", "Store", "GSTNumber", "StoreID", "VisitDate"])
            st.session_state.admin_df = load_from_supabase("admin_master", ["Username", "Password"])
            st.success("✅ Data refreshed successfully!")
            st.rerun()

# ====================== EMPLOYEE PANEL ======================
else:
    emp_code = st.session_state.emp_code
    emp_name = st.session_state.emp_name
    st.markdown(f"<h1 class='main-header'>👤 {emp_name}</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Your Beat Planning Dashboard</p>", unsafe_allow_html=True)
    
    employee_stores = st.session_state.gst_df[st.session_state.gst_df["EmployeeCode"].astype(str) == str(emp_code)]
    
    emp_menu = st.sidebar.radio(
        "Navigation", ["🎯 New Beat Plan", "📅 My Plans", "📆 Upcoming Plans", "📊 Analytics", "➕ Request New Store"]
    )
    
    if emp_menu == "🎯 New Beat Plan":
        st.markdown("<p class='sub-header'>Create Your Daily Beat Plan</p>", unsafe_allow_html=True)
        if employee_stores.empty:
            st.warning("⚠️ No stores assigned. Contact Admin.")
            st.stop()
        
        c1, c2, c3 = st.columns(3)
        with c1: visit_date = st.date_input("📅 Select Date", value=date.today(), key="beat_date")
        with c2: selected_cities = st.multiselect("🌍 Select Cities", sorted(employee_stores["City"].dropna().unique()), max_selections=3, key="city_multiselect")
        with c3:
            if st.button("🔍 Load Stores", use_container_width=True):
                st.session_state.selected_cities = selected_cities
        
        daily_plans = st.session_state.planned_df[
            (st.session_state.planned_df["EmployeeCode"].astype(str) == str(emp_code)) &
            (st.session_state.planned_df["VisitDate"] == visit_date)
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
            st.error("🚫 Maximum 10 stores reached for this Day")
        else:
            st.info(f"You can add {10 - planned_count} more stores this Day.")
        
        city_stores = employee_stores[employee_stores["City"].isin(st.session_state.selected_cities)] if st.session_state.selected_cities else employee_stores.copy()
        planned_ids = daily_plans["StoreID"].tolist()
        available = city_stores[~city_stores["StoreID"].isin(planned_ids)]
        
        st.markdown(f"### 🛍️ Available Stores ({len(available)})")
        if available.empty:
            st.info("No more stores available.")
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
                    if st.button("➕ Add", key=f"add_{idx}_{visit_date}"):
                        if planned_count < 10:
                            new_plan = pd.DataFrame([{
                                "EmployeeCode": emp_code, "EmployeeName": emp_name,
                                "City": row["City"], "Store": row["StoreName"],
                                "StoreID": row["StoreID"], "GSTNumber": row["GSTNumber"],
                                "VisitDate": visit_date
                            }])
                            st.session_state.planned_df = pd.concat([st.session_state.planned_df, new_plan], ignore_index=True)
                            if save_to_supabase("planned_visits", st.session_state.planned_df):
                                st.success(f"✅ {row['StoreName']} added!")
                                st.rerun()
        
        st.markdown("---")
        emp_plans = st.session_state.planned_df[st.session_state.planned_df["EmployeeCode"].astype(str) == str(emp_code)]
        download_beat_plan_button(emp_plans, "emp_download", "Beat_Plan")

    elif emp_menu == "📅 My Plans":
        my_plans = st.session_state.planned_df[st.session_state.planned_df["EmployeeCode"].astype(str) == str(emp_code)]
        if my_plans.empty:
            st.info("No plans yet.")
        else:
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Total Plans", len(my_plans))
            with c2: st.metric("Cities", my_plans['City'].nunique())
            with c3: st.metric("Dates", len(my_plans['VisitDate'].unique()))
            st.dataframe(my_plans.sort_values("VisitDate", ascending=False), use_container_width=True, hide_index=True)

    elif emp_menu == "📆 Upcoming Plans":
        upcoming = st.session_state.planned_df[
            (st.session_state.planned_df["EmployeeCode"].astype(str) == str(emp_code)) &
            (st.session_state.planned_df["VisitDate"] >= date.today())
        ].sort_values("VisitDate")
        if upcoming.empty:
            st.info("No upcoming visits.")
        else:
            for vdate in sorted(upcoming["VisitDate"].unique()):
                plans = upcoming[upcoming["VisitDate"] == vdate]
                st.markdown(f"**📅 {vdate.strftime('%A, %d %B %Y')}** ({len(plans)} stores)")
                for _, p in plans.iterrows():
                    st.markdown(f"• **{p['Store']}** - {p['City']}")

    elif emp_menu == "📊 Analytics":
        my_plans = st.session_state.planned_df[st.session_state.planned_df["EmployeeCode"].astype(str) == str(emp_code)]
        if my_plans.empty:
            st.info("No data yet.")
        else:
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Visits by City")
                st.bar_chart(my_plans.groupby("City").size())
            with c2:
                st.subheader("Visits Over Time")
                df_copy = my_plans.copy()
                df_copy["Month"] = pd.to_datetime(df_copy["VisitDate"]).dt.to_period("M").astype(str)
                st.line_chart(df_copy.groupby("Month").size())

    elif emp_menu == "➕ Request New Store":
        st.subheader("Request & Add New Store")
        with st.form("store_request"):
            c1, c2 = st.columns(2)
            with c1:
                sname = st.text_input("Store Name*")
                city = st.text_input("City*")
            with c2:
                gst = st.text_input("GST Number*", max_chars=15).upper().strip()
                reason = st.text_area("Reason / Remarks", height=100)
            if st.form_submit_button("✅ Add Store Now", type="primary"):
                if not sname or not city or not gst:
                    st.error("Store Name, City and GST are required!")
                elif not is_valid_gstin(gst):
                    st.error("Invalid GST Number format!")
                elif st.session_state.gst_df["GSTNumber"].astype(str).str.upper().eq(gst).any():
                    st.error("This GST Number already exists!")
                else:
                    next_id = f"S{len(st.session_state.gst_df)+1:05d}"
                    new_store = pd.DataFrame([{
                        "StoreID": next_id, "StoreName": sname.title(),
                        "GSTNumber": gst, "City": city.title(), "EmployeeCode": emp_code
                    }])
                    st.session_state.gst_df = pd.concat([st.session_state.gst_df, new_store], ignore_index=True)
                    if save_to_supabase("gst_master", st.session_state.gst_df):
                        st.success(f"✅ Store '{sname}' added successfully!")
                        st.rerun()

st.caption("Beat Plan Pro © 2026 | 🚀 Powered by Supabase (Data persists forever!)")
