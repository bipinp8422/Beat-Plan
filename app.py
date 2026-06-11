import streamlit as st
import pandas as pd
import os
import supabase
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

# ====================== SUPABASE CONNECTION ======================
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()

# ====================== HELPER: GSTIN VALIDATOR ======================
def is_valid_gstin(gstin):
    gstin = str(gstin).strip().upper()
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$'
    return bool(re.match(pattern, gstin))

def get_progress_color(current, max_val):
    percent = (current / max_val) * 100
    if percent >= 100: return "#ef4444"
    elif percent >= 80: return "#f59e0b"
    else: return "#10b981"

def download_beat_plan_button(df, key, filename_prefix="Beat_Plan"):
    if not df.empty:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        st.download_button(
            label="📥 Download Beat Plan (Excel)",
            data=output.getvalue(),
            file_name=f"{filename_prefix}_{date.today().strftime('%Y-%m-%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key=key
        )
    else:
        st.info("No plans to download for the selected filters.")

# ====================== SUPABASE DATA LOADERS ======================
def load_employees():
    data = supabase.table("employees").select("*").execute()
    df = pd.DataFrame(data.data) if data.data else pd.DataFrame(
        columns=["id", "EmployeeCode", "EmployeeName", "Password"])
    return df

def load_stores():
    data = supabase.table("stores").select("*").execute()
    df = pd.DataFrame(data.data) if data.data else pd.DataFrame(
        columns=["id", "StoreID", "StoreName", "GSTNumber", "City", "EmployeeCode"])
    return df

def load_admins():
    data = supabase.table("admins").select("*").execute()
    df = pd.DataFrame(data.data) if data.data else pd.DataFrame(
        columns=["id", "Username", "Password"])
    return df

def load_planned_df():
    data = supabase.table("planned_visits").select("*").execute()
    df = pd.DataFrame(data.data) if data.data else pd.DataFrame(
        columns=["id", "EmployeeCode", "EmployeeName", "City",
                 "Store", "GSTNumber", "StoreID", "VisitDate"])
    if not df.empty and "VisitDate" in df.columns:
        df["VisitDate"] = pd.to_datetime(df["VisitDate"], errors="coerce").dt.date
    return df

def save_visit(new_row: dict):
    """Insert a single new planned visit into Supabase."""
    try:
        new_row["VisitDate"] = str(new_row["VisitDate"])
        supabase.table("planned_visits").insert(new_row).execute()
        # Refresh session state
        st.session_state.planned_df = load_planned_df()
        return True
    except Exception as e:
        st.error(f"❌ Save failed: {e}")
        return False

def add_employee_db(emp_code, emp_name, password):
    supabase.table("employees").insert({
        "EmployeeCode": emp_code.upper(),
        "EmployeeName": emp_name.title(),
        "Password": password
    }).execute()
    st.session_state.employee_df = load_employees()

def add_store_db(store_id, store_name, gst_no, city, emp_code):
    supabase.table("stores").insert({
        "StoreID": store_id,
        "StoreName": store_name.title(),
        "GSTNumber": gst_no.upper(),
        "City": city.title(),
        "EmployeeCode": emp_code
    }).execute()
    st.session_state.gst_df = load_stores()

# ====================== LOAD DATA INTO SESSION STATE ======================
if "employee_df" not in st.session_state:
    st.session_state.employee_df = load_employees()
if "gst_df" not in st.session_state:
    st.session_state.gst_df = load_stores()
if "planned_df" not in st.session_state:
    st.session_state.planned_df = load_planned_df()
if "admin_df" not in st.session_state:
    st.session_state.admin_df = load_admins()

# ====================== SESSION STATE DEFAULTS ======================
for k, v in {"logged_in": False, "role": "", "emp_code": "",
             "emp_name": "", "selected_cities": []}.items():
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
            user = st.text_input("Username", placeholder="Enter admin username", key="admin_user")
            pwd  = st.text_input("Password", type="password", placeholder="Enter password", key="admin_pwd")
            if st.button("🔓 Login as Admin", type="primary", use_container_width=True):
                admin_df = st.session_state.admin_df
                match = admin_df[
                    (admin_df["Username"].astype(str) == user) &
                    (admin_df["Password"].astype(str) == pwd)
                ]
                if not match.empty:
                    st.session_state.logged_in = True
                    st.session_state.role = "admin"
                    st.success("✅ Admin login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials.")

        else:
            st.markdown("### Employee Login")
            emp_code = st.text_input("Employee Code", placeholder="e.g., EMP001", key="emp_code_login")
            pwd      = st.text_input("Password", type="password", placeholder="Enter password", key="emp_pwd_login")
            if st.button("🔓 Login as Employee", type="primary", use_container_width=True):
                emp_df = st.session_state.employee_df
                x = emp_df[
                    (emp_df["EmployeeCode"].astype(str) == emp_code) &
                    (emp_df["Password"].astype(str) == pwd)
                ]
                if not x.empty:
                    st.session_state.logged_in  = True
                    st.session_state.role       = "employee"
                    st.session_state.emp_code   = str(x.iloc[0]["EmployeeCode"])
                    st.session_state.emp_name   = x.iloc[0]["EmployeeName"]
                    st.success(f"✅ Welcome, {st.session_state.emp_name}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials.")
    st.stop()

# ====================== LOGOUT ======================
col1, col2, col3 = st.columns([10, 1, 1])
with col3:
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.update({
            "logged_in": False, "role": "", "emp_code": "",
            "emp_name": "", "selected_cities": []
        })
        st.rerun()

# ====================== ADMIN PANEL ======================
if st.session_state.role == "admin":
    st.markdown("<h1 class='main-header'>🛠️ Admin Dashboard</h1>", unsafe_allow_html=True)

    admin_menu = st.sidebar.radio(
        "Navigation",
        ["📊 Dashboard", "👥 Manage Employees", "🏪 Manage Stores",
         "📋 View Plans", "📤 Upload Masters"]
    )

    # ── Dashboard ────────────────────────────────────────────────────
    if admin_menu == "📊 Dashboard":
        # Refresh counts from Supabase
        total_emp    = len(st.session_state.employee_df)
        total_stores = len(st.session_state.gst_df)
        total_plans  = len(st.session_state.planned_df)
        today_plans  = len([
            d for d in st.session_state.planned_df["VisitDate"]
            if d == date.today()
        ])

        col1, col2, col3, col4 = st.columns(4)
        for col, icon, label, value in zip(
            [col1, col2, col3, col4],
            ["👥", "🏪", "📋", "📅"],
            ["Total Employees", "Total Stores", "Total Plans", "Today's Visits"],
            [total_emp, total_stores, total_plans, today_plans]
        ):
            with col:
                st.markdown(f"""
                    <div class='metric-card'>
                        <div style='font-size:32px;'>{icon}</div>
                        <div>{label}</div>
                        <div class='metric-value'>{value}</div>
                    </div>
                """, unsafe_allow_html=True)

        if st.button("🔄 Refresh Data"):
            st.session_state.employee_df = load_employees()
            st.session_state.gst_df      = load_stores()
            st.session_state.planned_df  = load_planned_df()
            st.rerun()

    # ── Manage Employees ─────────────────────────────────────────────
    elif admin_menu == "👥 Manage Employees":
        tab1, tab2 = st.tabs(["View Employees", "Add New Employee"])

        with tab1:
            if st.button("🔄 Refresh"):
                st.session_state.employee_df = load_employees()
                st.rerun()
            display_df = st.session_state.employee_df.drop(
                columns=["id", "Password"], errors="ignore")
            st.dataframe(display_df, use_container_width=True, hide_index=True)

        with tab2:
            with st.form("add_employee"):
                col1, col2 = st.columns(2)
                with col1:
                    new_emp_code = st.text_input("Employee Code", placeholder="EMP001")
                    new_emp_name = st.text_input("Employee Name", placeholder="John Doe")
                with col2:
                    new_emp_pwd = st.text_input("Password", type="password")

                if st.form_submit_button("➕ Add Employee", type="primary"):
                    if not new_emp_code or not new_emp_name or not new_emp_pwd:
                        st.error("All fields required!")
                    elif st.session_state.employee_df["EmployeeCode"].astype(str)\
                            .str.upper().eq(new_emp_code.upper()).any():
                        st.error("Employee code already exists!")
                    else:
                        try:
                            add_employee_db(new_emp_code, new_emp_name, new_emp_pwd)
                            st.success("✅ Employee added!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")

    # ── Manage Stores ─────────────────────────────────────────────────
    elif admin_menu == "🏪 Manage Stores":
        tab1, tab2 = st.tabs(["View Stores", "Add New Store"])

        with tab1:
            if st.button("🔄 Refresh"):
                st.session_state.gst_df = load_stores()
                st.rerun()
            display_df = st.session_state.gst_df.drop(columns=["id"], errors="ignore")
            st.dataframe(display_df, use_container_width=True, hide_index=True)

        with tab2:
            with st.form("add_store_admin"):
                col1, col2 = st.columns(2)
                with col1:
                    store_name   = st.text_input("Store Name")
                    gst_no       = st.text_input("GST Number", max_chars=15).upper().strip()
                with col2:
                    city         = st.text_input("City")
                    emp_options  = st.session_state.employee_df["EmployeeCode"].unique().tolist()
                    emp_code_sel = st.selectbox(
                        "Assign Employee",
                        emp_options if emp_options else ["No Employees"]
                    )

                if st.form_submit_button("➕ Add Store", type="primary"):
                    if not store_name or not gst_no or not city:
                        st.error("All fields required!")
                    elif not is_valid_gstin(gst_no):
                        st.error("Invalid GST Number!")
                    elif st.session_state.gst_df["GSTNumber"].astype(str)\
                            .str.upper().eq(gst_no).any():
                        st.error("GST already exists!")
                    else:
                        try:
                            next_id = f"S{len(st.session_state.gst_df)+1:05d}"
                            add_store_db(next_id, store_name, gst_no, city, emp_code_sel)
                            st.success("✅ Store added!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")

    # ── View Plans ────────────────────────────────────────────────────
    elif admin_menu == "📋 View Plans":
        st.subheader("All Visit Plans")

        if st.button("🔄 Refresh Plans"):
            st.session_state.planned_df = load_planned_df()
            st.rerun()

        col1, col2, col3 = st.columns(3)
        with col1:
            filter_emp = st.selectbox(
                "Filter by Employee",
                ["All"] + list(st.session_state.planned_df["EmployeeName"].dropna().unique())
            )
        with col2:
            filter_city = st.selectbox(
                "Filter by City",
                ["All"] + list(st.session_state.planned_df["City"].dropna().unique())
            )
        with col3:
            date_range = st.date_input(
                "Filter by Date",
                value=(date.today() - timedelta(days=30), date.today())
            )

        filtered = st.session_state.planned_df.copy()
        if filter_emp  != "All":
            filtered = filtered[filtered["EmployeeName"] == filter_emp]
        if filter_city != "All":
            filtered = filtered[filtered["City"] == filter_city]
        if len(date_range) == 2:
            start, end = date_range
            filtered = filtered[
                (filtered["VisitDate"] >= start) &
                (filtered["VisitDate"] <= end)
            ]

        display_filtered = filtered.drop(columns=["id"], errors="ignore")
        st.dataframe(
            display_filtered.sort_values("VisitDate", ascending=False),
            use_container_width=True, hide_index=True
        )

        st.markdown("---")
        download_beat_plan_button(
            df=display_filtered.sort_values("VisitDate", ascending=False),
            key="admin_beat_plan_download",
            filename_prefix="Beat_Plan_Admin"
        )

    # ── Upload Masters ────────────────────────────────────────────────
    elif admin_menu == "📤 Upload Masters":
        st.info("Upload Excel files to bulk-import data into Supabase. Existing records will be replaced.")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("👥 Employee Master")
            st.caption("Columns: EmployeeCode, EmployeeName, Password")
            uploaded_emp = st.file_uploader("Upload Employee Excel", type="xlsx", key="emp_up")
            if uploaded_emp and st.button("Upload Employees"):
                try:
                    df = pd.read_excel(uploaded_emp)
                    records = df[["EmployeeCode", "EmployeeName", "Password"]].to_dict(orient="records")
                    supabase.table("employees").delete().neq("id", 0).execute()
                    supabase.table("employees").insert(records).execute()
                    st.session_state.employee_df = load_employees()
                    st.success(f"✅ {len(records)} employees uploaded!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Upload failed: {e}")

        with col2:
            st.subheader("🏪 Store Master")
            st.caption("Columns: StoreID, StoreName, GSTNumber, City, EmployeeCode")
            uploaded_store = st.file_uploader("Upload Store Excel", type="xlsx", key="store_up")
            if uploaded_store and st.button("Upload Stores"):
                try:
                    df = pd.read_excel(uploaded_store)
                    records = df[["StoreID", "StoreName", "GSTNumber", "City", "EmployeeCode"]].to_dict(orient="records")
                    supabase.table("stores").delete().neq("id", 0).execute()
                    supabase.table("stores").insert(records).execute()
                    st.session_state.gst_df = load_stores()
                    st.success(f"✅ {len(records)} stores uploaded!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Upload failed: {e}")

        with col3:
            st.subheader("📋 Planned Visits")
            st.caption("Columns: EmployeeCode, EmployeeName, City, Store, GSTNumber, StoreID, VisitDate")
            uploaded_plans = st.file_uploader("Upload Planned Visits", type="xlsx", key="planned_up")
            if uploaded_plans and st.button("Upload Planned Visits"):
                try:
                    df = pd.read_excel(uploaded_plans)
                    df["VisitDate"] = pd.to_datetime(df["VisitDate"], errors="coerce").dt.date.astype(str)
                    records = df[[
                        "EmployeeCode", "EmployeeName", "City",
                        "Store", "GSTNumber", "StoreID", "VisitDate"
                    ]].to_dict(orient="records")
                    supabase.table("planned_visits").delete().neq("id", 0).execute()
                    supabase.table("planned_visits").insert(records).execute()
                    st.session_state.planned_df = load_planned_df()
                    st.success(f"✅ {len(records)} visits uploaded!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Upload failed: {e}")

# ====================== EMPLOYEE PANEL ======================
else:
    emp_code = st.session_state.emp_code
    emp_name = st.session_state.emp_name

    st.markdown(f"<h1 class='main-header'>👤 {emp_name}</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Your Beat Planning Dashboard</p>", unsafe_allow_html=True)

    employee_stores = st.session_state.gst_df[
        st.session_state.gst_df["EmployeeCode"].astype(str) == str(emp_code)
    ]

    emp_menu = st.sidebar.radio(
        "Navigation",
        ["🎯 New Beat Plan", "📅 My Plans", "📆 Upcoming Plans",
         "📊 Analytics", "➕ Request New Store"]
    )

    # ── New Beat Plan ─────────────────────────────────────────────────
    if emp_menu == "🎯 New Beat Plan":
        st.markdown("<p class='sub-header'>Create Your Daily Beat Plan</p>", unsafe_allow_html=True)

        if employee_stores.empty:
            st.warning("⚠️ No stores assigned. Contact Admin.")
            st.stop()

        col1, col2, col3 = st.columns(3)
        with col1:
            visit_date = st.date_input("📅 Select Date", value=date.today(), key="beat_date")
        with col2:
            selected_cities = st.multiselect(
                "🌍 Select Cities",
                sorted(employee_stores["City"].dropna().unique()),
                max_selections=3,
                key="city_multiselect"
            )
        with col3:
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
                    <div style='width:{min(planned_count*10,100)}%;height:100%;
                         background:{progress_color};border-radius:10px;'></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if planned_count >= 10:
            st.error("🚫 Maximum 10 stores reached for this day.")
        else:
            st.info(f"You can add {10 - planned_count} more stores today.")

        city_filter = st.session_state.selected_cities
        city_stores = (
            employee_stores[employee_stores["City"].isin(city_filter)].copy()
            if city_filter else employee_stores.copy()
        )
        planned_ids = daily_plans["StoreID"].tolist()
        available   = city_stores[~city_stores["StoreID"].isin(planned_ids)]

        st.markdown(f"### 🛍️ Available Stores ({len(available)})")
        if available.empty:
            st.info("No more stores available for the selected filters.")
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
                            ok = save_visit({
                                "EmployeeCode": emp_code,
                                "EmployeeName": emp_name,
                                "City":         row["City"],
                                "Store":        row["StoreName"],
                                "StoreID":      row["StoreID"],
                                "GSTNumber":    row["GSTNumber"],
                                "VisitDate":    visit_date
                            })
                            if ok:
                                st.success(f"✅ {row['StoreName']} added!")
                                st.rerun()

        st.markdown("---")
        emp_plans = st.session_state.planned_df[
            st.session_state.planned_df["EmployeeCode"].astype(str) == str(emp_code)
        ].drop(columns=["id"], errors="ignore")
        download_beat_plan_button(
            df=emp_plans,
            key="beat_plan_download",
            filename_prefix="Beat_Plan"
        )

    # ── My Plans ──────────────────────────────────────────────────────
    elif emp_menu == "📅 My Plans":
        if st.button("🔄 Refresh"):
            st.session_state.planned_df = load_planned_df()
            st.rerun()

        my_plans = st.session_state.planned_df[
            st.session_state.planned_df["EmployeeCode"].astype(str) == str(emp_code)
        ]
        if my_plans.empty:
            st.info("No plans yet.")
        else:
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("Total Plans", len(my_plans))
            with col2: st.metric("Cities",      my_plans["City"].nunique())
            with col3: st.metric("Dates",       len(my_plans["VisitDate"].unique()))

            display_df = my_plans.drop(columns=["id"], errors="ignore")
            st.dataframe(
                display_df.sort_values("VisitDate", ascending=False),
                use_container_width=True, hide_index=True
            )

    # ── Upcoming Plans ────────────────────────────────────────────────
    elif emp_menu == "📆 Upcoming Plans":
        if st.button("🔄 Refresh"):
            st.session_state.planned_df = load_planned_df()
            st.rerun()

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
                    st.markdown(f"• **{p['Store']}** — {p['City']}")

    # ── Analytics ─────────────────────────────────────────────────────
    elif emp_menu == "📊 Analytics":
        if st.button("🔄 Refresh"):
            st.session_state.planned_df = load_planned_df()
            st.rerun()

        my_plans = st.session_state.planned_df[
            st.session_state.planned_df["EmployeeCode"].astype(str) == str(emp_code)
        ]
        if my_plans.empty:
            st.info("No data yet.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Visits by City")
                st.bar_chart(my_plans.groupby("City").size())
            with col2:
                st.subheader("Visits by Month")
                mp = my_plans.copy()
                mp["Month"] = pd.to_datetime(mp["VisitDate"]).dt.to_period("M").astype(str)
                st.line_chart(mp.groupby("Month").size())

    # ── Request New Store ─────────────────────────────────────────────
    elif emp_menu == "➕ Request New Store":
        st.subheader("➕ Add New Store")
        with st.form("store_request"):
            col1, col2 = st.columns(2)
            with col1:
                sname  = st.text_input("Store Name*")
                city   = st.text_input("City*")
            with col2:
                gst    = st.text_input("GST Number*", max_chars=15).upper().strip()
                reason = st.text_area("Reason / Remarks", height=100)

            if st.form_submit_button("✅ Add Store Now", type="primary"):
                if not sname or not city or not gst:
                    st.error("Store Name, City and GST are required!")
                elif not is_valid_gstin(gst):
                    st.error("Invalid GST Number format!")
                elif st.session_state.gst_df["GSTNumber"].astype(str)\
                        .str.upper().eq(gst).any():
                    st.error("This GST Number already exists!")
                else:
                    try:
                        next_id = f"S{len(st.session_state.gst_df)+1:05d}"
                        add_store_db(next_id, sname, gst, city, emp_code)
                        st.success(f"✅ Store '{sname}' added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

st.caption("Beat Plan Pro © 2026 | Powered by Supabase")
