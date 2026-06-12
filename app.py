import streamlit as st
import pandas as pd
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
SUPABASE_URL = "https://kueicdruccvbempjvxzn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt1ZWljZHJ1Y2N2YmVtcGp2eHpuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODExMjE0MTcsImV4cCI6MjA5NjY5NzQxN30.aWkQ85Wq-iP2Gp1W1dfoATdRhR0rFcc1H6CGtK_zDE0"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"❌ Failed to connect to Supabase: {e}")
    st.stop()

# ====================== STYLING ======================
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); }
    .main-header {
        font-size: 48px; font-weight: 900;
        background: linear-gradient(90deg, #0066cc, #00a8e8, #00d4ff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin: 20px 0 10px 0; letter-spacing: -1px;
    }
    .sub-header { text-align: center; color: #475569; font-size: 16px; margin-bottom: 30px; font-weight: 600; }
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 24px; border-radius: 16px; border: 2px solid #e2e8f0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08); margin-bottom: 16px;
    }
    .store-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 20px; border-radius: 16px; border: 2px solid #e2e8f0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08); margin-bottom: 12px;
    }
    .progress-section {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 24px; border-radius: 16px; border: 2px solid #e2e8f0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08); margin-bottom: 20px;
    }
    .metric-value {
        font-size: 36px; font-weight: 800;
        background: linear-gradient(135deg, #0066cc, #00a8e8);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .stButton > button {
        border-radius: 12px; height: 48px; font-weight: 700;
        background: linear-gradient(90deg, #0066cc, #00a8e8) !important;
        color: white !important; border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ====================== COLUMN NAME NORMALIZER ======================
# Supabase may return lowercase column names depending on how tables were created.
# This maps any variant back to the PascalCase names used throughout the app.
COLUMN_MAP = {
    "EmployeeCode": ["employeecode", "employee_code"],
    "EmployeeName": ["employeename", "employee_name"],
    "Password":     ["password"],
    "StoreID":      ["storeid", "store_id"],
    "StoreName":    ["storename", "store_name"],
    "GSTNumber":    ["gstnumber", "gst_number", "gstnumber"],
    "City":         ["city"],
    "Store":        ["store"],
    "VisitDate":    ["visitdate", "visit_date"],
    "Username":     ["username"],
}

def normalize_columns(df):
    rename = {}
    lower_map = {c.lower().replace("_", ""): c for c in df.columns}
    for expected, variants in COLUMN_MAP.items():
        if expected in df.columns:
            continue
        for v in variants:
            key = v.lower().replace("_", "")
            if key in lower_map:
                rename[lower_map[key]] = expected
                break
    return df.rename(columns=rename) if rename else df

# ====================== DATABASE FUNCTIONS ======================
def init_db():
    try:
        supabase.table("planned_visits").select("*").limit(1).execute()
        return True
    except Exception as e:
        st.error(f"❌ Supabase connection failed: {e}")
        return False

def clean_dataframe(df, expected_columns):
    if df.empty:
        return df
    df = normalize_columns(df)
    for col in expected_columns:
        if col not in df.columns:
            df[col] = ""
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()
    if "VisitDate" in df.columns:
        df["VisitDate"] = pd.to_datetime(df["VisitDate"], errors="coerce").dt.date
    return df

def load_from_supabase(table_name, columns):
    try:
        all_rows = []
        batch_size = 1000
        offset = 0
        while True:
            response = supabase.table(table_name).select("*").range(offset, offset + batch_size - 1).execute()
            if not response.data:
                break
            all_rows.extend(response.data)
            if len(response.data) < batch_size:
                break  # last page
            offset += batch_size
        if all_rows:
            df = pd.DataFrame(all_rows)
            return clean_dataframe(df, columns)
        return pd.DataFrame(columns=columns)
    except Exception as e:
        st.warning(f"⚠️ Error loading `{table_name}`: {e}")
        return pd.DataFrame(columns=columns)

def save_to_supabase(table_name, df):
    try:
        df_copy = df.copy()
        if "id" in df_copy.columns:
            df_copy = df_copy.drop("id", axis=1)
        for col in df_copy.columns:
            if col == "VisitDate" or pd.api.types.is_datetime64_any_dtype(df_copy[col]):
                df_copy[col] = pd.to_datetime(df_copy[col]).dt.strftime("%Y-%m-%d")
        try:
            supabase.table(table_name).delete().neq("id", -1).execute()
        except Exception:
            pass
        if not df_copy.empty:
            records = df_copy.to_dict("records")
            for i in range(0, len(records), 100):
                supabase.table(table_name).insert(records[i:i+100]).execute()
        return True
    except Exception as e:
        st.error(f"❌ Save failed for `{table_name}`: {e}")
        return False

# ====================== COLUMN CONSTANTS ======================
EMP_COLS   = ["EmployeeCode", "EmployeeName", "Password"]
GST_COLS   = ["StoreID", "StoreName", "GSTNumber", "City", "EmployeeCode"]
PLAN_COLS  = ["EmployeeCode", "EmployeeName", "City", "Store", "GSTNumber", "StoreID", "VisitDate"]
ADMIN_COLS = ["Username", "Password"]

# ====================== INITIALIZE ======================
if not init_db():
    st.stop()

if "employee_df" not in st.session_state:
    st.session_state.employee_df = load_from_supabase("employee_master", EMP_COLS)
if "gst_df" not in st.session_state:
    st.session_state.gst_df = load_from_supabase("gst_master", GST_COLS)
if "planned_df" not in st.session_state:
    st.session_state.planned_df = load_from_supabase("planned_visits", PLAN_COLS)
if "admin_df" not in st.session_state:
    st.session_state.admin_df = load_from_supabase("admin_master", ADMIN_COLS)

# ====================== SESSION STATE ======================
for k, v in {"logged_in": False, "role": "", "emp_code": "", "emp_name": "", "selected_cities": []}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ====================== HELPERS ======================
def is_valid_gstin(gstin):
    return bool(re.match(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$", str(gstin).strip().upper()))

def get_progress_color(current, max_val):
    pct = (current / max_val) * 100
    return "#ef4444" if pct >= 100 else "#f59e0b" if pct >= 80 else "#10b981"

def safe_col(df, col):
    return df[col] if col in df.columns else pd.Series([""] * len(df))

def download_beat_plan_button(df, key, filename_prefix="Beat_Plan"):
    if not df.empty:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Beat Plan")
        output.seek(0)
        st.download_button(
            label="📥 Download Beat Plan (Excel)",
            data=output.getvalue(),
            file_name=f"{filename_prefix}_{date.today().strftime('%Y-%m-%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key=key,
        )

# ====================== LOGIN PAGE ======================
if not st.session_state.logged_in:
    st.markdown("<h1 class='main-header'>🚀 Beat Plan Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Smart Store Visit Planning System</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        login_type = st.radio("Login Type", ["👨‍💼 Admin", "👷 Employee"], horizontal=True)

        if login_type == "👨‍💼 Admin":
            st.markdown("### Admin Login")
            user = st.text_input("Username", key="admin_user")
            pwd  = st.text_input("Password", type="password", key="admin_pwd")
            if st.button("🔓 Login as Admin", type="primary", use_container_width=True):
                if not user or not pwd:
                    st.error("❌ Enter both fields.")
                else:
                    df = st.session_state.admin_df.copy()
                    if "Username" not in df.columns or "Password" not in df.columns:
                        st.error("❌ admin_master columns missing. See debug expander above.")
                    else:
                        match = (
                            (df["Username"].astype(str).str.strip() == user.strip()) &
                            (df["Password"].astype(str).str.strip() == pwd.strip())
                        )
                        if match.any():
                            st.session_state.logged_in = True
                            st.session_state.role = "admin"
                            st.rerun()
                        else:
                            st.error(f"❌ Invalid credentials. ({len(df)} admin record(s) in DB)")
        else:
            st.markdown("### Employee Login")
            emp_in = st.text_input("Employee Code", key="emp_code_login")
            pwd_in = st.text_input("Password", type="password", key="emp_pwd_login")
            if st.button("🔓 Login as Employee", type="primary", use_container_width=True):
                if not emp_in or not pwd_in:
                    st.error("❌ Enter both fields.")
                else:
                    df = st.session_state.employee_df.copy()
                    if "EmployeeCode" not in df.columns or "Password" not in df.columns:
                        st.error("❌ employee_master columns missing. See debug expander above.")
                    else:
                        match = df[
                            (df["EmployeeCode"].astype(str).str.strip() == emp_in.strip()) &
                            (df["Password"].astype(str).str.strip()     == pwd_in.strip())
                        ]
                        if not match.empty:
                            st.session_state.logged_in = True
                            st.session_state.role      = "employee"
                            st.session_state.emp_code  = str(match.iloc[0]["EmployeeCode"])
                            st.session_state.emp_name  = match.iloc[0]["EmployeeName"]
                            st.rerun()
                        else:
                            st.error(f"❌ Invalid credentials. ({len(df)} employee record(s) in DB)")
    st.stop()

# ====================== LOGOUT ======================
c1, c2, c3 = st.columns([10, 1, 1])
with c3:
    if st.button("🚪 Logout", use_container_width=True):
        for k, v in {"logged_in": False, "role": "", "emp_code": "", "emp_name": "", "selected_cities": []}.items():
            st.session_state[k] = v
        st.rerun()

# ====================== ADMIN PANEL ======================
if st.session_state.role == "admin":
    st.markdown("<h1 class='main-header'>🛠️ Admin Dashboard</h1>", unsafe_allow_html=True)

    admin_menu = st.sidebar.radio(
        "Navigation",
        ["📊 Dashboard", "👥 Manage Employees", "🏪 Manage Stores", "📋 View Plans", "🔄 Refresh Data"],
    )

    if admin_menu == "📊 Dashboard":
        today_plans = int((st.session_state.planned_df["VisitDate"] == date.today()).sum()) \
            if "VisitDate" in st.session_state.planned_df.columns else 0

        cols = st.columns(4)
        for col, (icon, label, val) in zip(cols, [
            ("👥", "Total Employees", len(st.session_state.employee_df)),
            ("🏪", "Total Stores",    len(st.session_state.gst_df)),
            ("📋", "Total Plans",     len(st.session_state.planned_df)),
            ("📅", "Today's Visits",  today_plans),
        ]):
            with col:
                st.markdown(f"""
                    <div class='metric-card'>
                        <div style='font-size:32px;margin-bottom:8px;'>{icon}</div>
                        <div style='color:#64748b;font-size:14px;font-weight:600;'>{label}</div>
                        <div class='metric-value'>{val}</div>
                    </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("Recent Plans")
        if not st.session_state.planned_df.empty:
            st.dataframe(
                st.session_state.planned_df.sort_values("VisitDate", ascending=False).head(10)
                if "VisitDate" in st.session_state.planned_df.columns
                else st.session_state.planned_df.head(10),
                use_container_width=True, hide_index=True,
            )
        else:
            st.info("No plans yet.")

    elif admin_menu == "👥 Manage Employees":
        tab1, tab2, tab3 = st.tabs(["👁️ View", "➕ Add", "🗑️ Delete"])
        with tab1:
            disp = st.session_state.employee_df.drop(columns=["Password"], errors="ignore")
            if not disp.empty:
                st.dataframe(disp, use_container_width=True, hide_index=True)
            else:
                st.info("No employees found.")
        with tab2:
            with st.form("add_emp"):
                c1, c2 = st.columns(2)
                with c1:
                    ecode = st.text_input("Employee Code*")
                    ename = st.text_input("Employee Name*")
                with c2:
                    epwd = st.text_input("Password*", type="password")
                if st.form_submit_button("➕ Add Employee", type="primary"):
                    if not ecode or not ename or not epwd:
                        st.error("All fields required!")
                    elif safe_col(st.session_state.employee_df, "employeecode").astype(str).str.upper().eq(ecode.strip().upper()).any():
                        st.error("❌ Code already exists!")
                    else:
                        new_row = pd.DataFrame([{"employeecode": ecode.strip().upper(), "EmployeeName": ename.strip().title(), "Password": epwd.strip()}])
                        st.session_state.employee_df = pd.concat([st.session_state.employee_df, new_row], ignore_index=True)
                        if save_to_supabase("employee_master", st.session_state.employee_df):
                            st.success("✅ Added!"); st.rerun()
        with tab3:
            if st.session_state.employee_df.empty:
                st.info("No employees.")
            else:
                emp_del = st.selectbox("Select", safe_col(st.session_state.employee_df, "employeecode").unique())
                if st.button("🗑️ Delete", type="primary"):
                    st.session_state.employee_df = st.session_state.employee_df[
                        safe_col(st.session_state.employee_df, "Employeecode") != emp_del]
                    if save_to_supabase("employee_master", st.session_state.employee_df):
                        st.success(f"✅ {emp_del} deleted!"); st.rerun()

    elif admin_menu == "🏪 Manage Stores":
        tab1, tab2, tab3 = st.tabs(["👁️ View", "➕ Add", "🗑️ Delete"])
        with tab1:
            if not st.session_state.gst_df.empty:
                st.dataframe(st.session_state.gst_df, use_container_width=True, hide_index=True)
            else:
                st.info("No stores found.")
        with tab2:
            with st.form("add_store"):
                c1, c2 = st.columns(2)
                with c1:
                    sname = st.text_input("Store Name*")
                    gstno = st.text_input("GST Number*", max_chars=15)
                with c2:
                    city  = st.text_input("City*")
                    emp_opts = safe_col(st.session_state.employee_df, "employeecode").unique().tolist() or ["—"]
                    emp_sel  = st.selectbox("Assign to Employee*", emp_opts)
                if st.form_submit_button("➕ Add Store", type="primary"):
                    gc = gstno.strip().upper()
                    if not sname or not gc or not city:
                        st.error("All fields required!")
                    elif not is_valid_gstin(gc):
                        st.error("❌ Invalid GST! e.g. 22AAAAA0000A1Z5")
                    elif safe_col(st.session_state.gst_df, "GSTNumber").astype(str).str.upper().eq(gc).any():
                        st.error("❌ GST exists!")
                    else:
                        nid = f"S{len(st.session_state.gst_df)+1:05d}"
                        st.session_state.gst_df = pd.concat([st.session_state.gst_df,
                            pd.DataFrame([{"StoreID": nid, "StoreName": sname.strip().title(),
                                           "GSTNumber": gc, "City": city.strip().title(), "employeecode": emp_sel}])
                        ], ignore_index=True)
                        if save_to_supabase("gst_master", st.session_state.gst_df):
                            st.success("✅ Store added!"); st.rerun()
        with tab3:
            if st.session_state.gst_df.empty:
                st.info("No stores.")
            else:
                sdel = st.selectbox("Select Store", safe_col(st.session_state.gst_df, "StoreID").unique())
                if st.button("🗑️ Delete Store", type="primary"):
                    st.session_state.gst_df = st.session_state.gst_df[safe_col(st.session_state.gst_df, "StoreID") != sdel]
                    if save_to_supabase("gst_master", st.session_state.gst_df):
                        st.success(f"✅ {sdel} deleted!"); st.rerun()

    elif admin_menu == "📋 View Plans":
        st.subheader("All Visit Plans")
        c1, c2, c3 = st.columns(3)
        with c1: femp  = st.selectbox("Employee", ["All"] + list(safe_col(st.session_state.planned_df, "EmployeeName").dropna().unique()))
        with c2: fcity = st.selectbox("City",     ["All"] + list(safe_col(st.session_state.planned_df, "City").dropna().unique()))
        with c3: drange = st.date_input("Date Range", value=(date.today()-timedelta(days=30), date.today()))

        fp = st.session_state.planned_df.copy()
        if femp  != "All" and "EmployeeName" in fp.columns: fp = fp[fp["EmployeeName"] == femp]
        if fcity != "All" and "City"         in fp.columns: fp = fp[fp["City"]          == fcity]
        if isinstance(drange, (list, tuple)) and len(drange) == 2 and "VisitDate" in fp.columns:
            fp = fp[(fp["VisitDate"] >= drange[0]) & (fp["VisitDate"] <= drange[1])]

        st.markdown(f"**{len(fp)} record(s)**")
        st.dataframe(fp.sort_values("VisitDate", ascending=False) if "VisitDate" in fp.columns else fp,
                     use_container_width=True, hide_index=True)
        download_beat_plan_button(fp, "admin_dl", "Beat_Plan_Admin")

    elif admin_menu == "🔄 Refresh Data":
        st.info("Syncs latest data from Supabase.")
        if st.button("🔄 Refresh", type="primary", use_container_width=True):
            st.session_state.employee_df = load_from_supabase("employee_master", EMP_COLS)
            st.session_state.gst_df      = load_from_supabase("gst_master",      GST_COLS)
            st.session_state.planned_df  = load_from_supabase("planned_visits",  PLAN_COLS)
            st.session_state.admin_df    = load_from_supabase("admin_master",    ADMIN_COLS)
            st.success("✅ Refreshed!"); st.rerun()

# ====================== EMPLOYEE PANEL ======================
else:
    emp_code = st.session_state.emp_code
    emp_name = st.session_state.emp_name

    st.markdown(f"<h1 class='main-header'>👤 {emp_name}</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Your Beat Planning Dashboard</p>", unsafe_allow_html=True)

    employee_stores = st.session_state.gst_df[
        safe_col(st.session_state.gst_df, "employeecode").astype(str) == str(emp_code)
    ] if not st.session_state.gst_df.empty else pd.DataFrame(columns=GST_COLS)

    emp_menu = st.sidebar.radio(
        "Navigation",
        ["🎯 New Beat Plan", "📅 My Plans", "📆 Upcoming Plans", "📊 Analytics", "➕ Request New Store"],
    )

    if emp_menu == "🎯 New Beat Plan":
        if employee_stores.empty:
            st.warning("⚠️ No stores assigned. Contact Admin.")
            st.stop()

        c1, c2, c3 = st.columns(3)
        with c1: visit_date = st.date_input("📅 Date", value=date.today(), key="beat_date")
        with c2:
            city_opts = sorted(safe_col(employee_stores, "City").dropna().unique().tolist())
            sel_cities = st.multiselect("🌍 Cities (max 3)", city_opts, max_selections=3, key="city_ms")
        with c3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔍 Load Stores", use_container_width=True):
                st.session_state.selected_cities = sel_cities

        daily_plans = st.session_state.planned_df[
            (safe_col(st.session_state.planned_df, "employeecode").astype(str) == str(emp_code)) &
            (st.session_state.planned_df["VisitDate"] == visit_date)
        ] if "VisitDate" in st.session_state.planned_df.columns else pd.DataFrame(columns=PLAN_COLS)

        pc    = len(daily_plans)
        pcol  = get_progress_color(pc, 10)

        st.markdown(f"""
            <div class='progress-section'>
                <div style='display:flex;justify-content:space-between;margin-bottom:10px;'>
                    <span style='font-weight:700;font-size:16px;'>Daily Progress</span>
                    <span style='font-weight:800;color:{pcol};font-size:18px;'>{pc}/10</span>
                </div>
                <div style='height:10px;background:#e2e8f0;border-radius:10px;overflow:hidden;'>
                    <div style='width:{min(pc*10,100)}%;height:100%;background:{pcol};border-radius:10px;'></div>
                </div>
                <div style='margin-top:8px;color:#64748b;font-size:13px;'>
                    {"🚫 Maximum 10 stores reached." if pc >= 10 else f"✅ {10-pc} more store(s) can be added."}
                </div>
            </div>""", unsafe_allow_html=True)

        if not daily_plans.empty:
            with st.expander(f"✅ Already planned for {visit_date} ({pc} stores)"):
                show = [c for c in ["Store","City","GSTNumber"] if c in daily_plans.columns]
                st.dataframe(daily_plans[show], use_container_width=True, hide_index=True)

        if pc < 10:
            show_cities = st.session_state.selected_cities or safe_col(employee_stores, "City").unique().tolist()
            city_stores = employee_stores[safe_col(employee_stores, "City").isin(show_cities)]
            planned_ids = safe_col(daily_plans, "StoreID").tolist()
            available   = city_stores[~safe_col(city_stores, "StoreID").isin(planned_ids)]

            st.markdown(f"### 🛍️ Available Stores ({len(available)})")
            if available.empty:
                st.info("No more stores available for selected cities.")
            else:
                for idx, row in available.iterrows():
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f"""
                            <div class='store-card'>
                                <div style='font-weight:700;font-size:18px;color:#1e293b;'>
                                    🏪 {row.get('StoreName','—')}
                                </div>
                                <div style='margin-top:10px;color:#475569;line-height:1.8;'>
                                    <strong>ID:</strong> {row.get('StoreID','—')} &nbsp;
                                    <strong>City:</strong> {row.get('City','—')} &nbsp;
                                    <strong>GST:</strong> {row.get('GSTNumber','—')}
                                </div>
                            </div>""", unsafe_allow_html=True)
                    with col2:
                        st.markdown("<br><br>", unsafe_allow_html=True)
                        if st.button("➕ Add", key=f"add_{idx}_{visit_date}"):
                            new_plan = pd.DataFrame([{
                                "employeecode": emp_code, "EmployeeName": emp_name,
                                "City": row.get("City",""), "Store": row.get("StoreName",""),
                                "StoreID": row.get("StoreID",""), "GSTNumber": row.get("GSTNumber",""),
                                "VisitDate": visit_date,
                            }])
                            st.session_state.planned_df = pd.concat(
                                [st.session_state.planned_df, new_plan], ignore_index=True)
                            if save_to_supabase("planned_visits", st.session_state.planned_df):
                                st.success(f"✅ {row.get('StoreName','')} added!"); st.rerun()

        st.markdown("---")
        emp_plans = st.session_state.planned_df[
            safe_col(st.session_state.planned_df, "EmployeeCode").astype(str) == str(emp_code)]
        download_beat_plan_button(emp_plans, "emp_dl", f"Beat_Plan_{emp_code}")

    elif emp_menu == "📅 My Plans":
        my = st.session_state.planned_df[
            safe_col(st.session_state.planned_df, "EmployeeCode").astype(str) == str(emp_code)]
        if my.empty:
            st.info("No plans yet.")
        else:
            c1,c2,c3 = st.columns(3)
            with c1: st.metric("Total Plans",  len(my))
            with c2: st.metric("Cities",       safe_col(my,"City").nunique())
            with c3: st.metric("Unique Dates", len(safe_col(my,"VisitDate").unique()))
            st.dataframe(my.sort_values("VisitDate",ascending=False) if "VisitDate" in my.columns else my,
                         use_container_width=True, hide_index=True)
            download_beat_plan_button(my, "my_dl", f"My_Plans_{emp_code}")

    elif emp_menu == "📆 Upcoming Plans":
        if "VisitDate" not in st.session_state.planned_df.columns:
            st.info("No upcoming visits.")
        else:
            upcoming = st.session_state.planned_df[
                (safe_col(st.session_state.planned_df,"EmployeeCode").astype(str) == str(emp_code)) &
                (st.session_state.planned_df["VisitDate"] >= date.today())
            ].sort_values("VisitDate")
            if upcoming.empty:
                st.info("No upcoming visits.")
            else:
                for vdate in sorted(upcoming["VisitDate"].unique()):
                    plans = upcoming[upcoming["VisitDate"] == vdate]
                    label = "🟢 Today" if vdate == date.today() else ""
                    st.markdown(f"""
                        <div style='background:#f0f9ff;border-left:4px solid #0066cc;
                             padding:12px 16px;border-radius:8px;margin-bottom:8px;'>
                            <strong>📅 {vdate.strftime('%A, %d %B %Y')}</strong>
                            &nbsp;<span style='color:#0066cc;font-size:13px;'>{label}</span>
                            &nbsp;— {len(plans)} store(s)
                        </div>""", unsafe_allow_html=True)
                    for _, p in plans.iterrows():
                        st.markdown(f"&nbsp;&nbsp;&nbsp;• **{p.get('Store','—')}** — {p.get('City','—')}")

    elif emp_menu == "📊 Analytics":
        my = st.session_state.planned_df[
            safe_col(st.session_state.planned_df,"employeecode").astype(str) == str(emp_code)]
        if my.empty:
            st.info("No data yet.")
        else:
            c1,c2,c3,c4 = st.columns(4)
            with c1: st.metric("Total Visits", len(my))
            with c2: st.metric("Cities",       safe_col(my,"City").nunique())
            with c3: st.metric("Stores",       safe_col(my,"Store").nunique())
            with c4:
                tm = my[pd.to_datetime(safe_col(my,"VisitDate"),errors="coerce").dt.month == date.today().month] \
                    if "VisitDate" in my.columns else pd.DataFrame()
                st.metric("This Month", len(tm))
            st.markdown("---")
            c1,c2 = st.columns(2)
            with c1:
                st.subheader("Visits by City")
                if "City" in my.columns: st.bar_chart(my.groupby("City").size())
            with c2:
                st.subheader("Visits Over Time")
                if "VisitDate" in my.columns:
                    tmp = my.copy()
                    tmp["Month"] = pd.to_datetime(tmp["VisitDate"],errors="coerce").dt.to_period("M").astype(str)
                    st.line_chart(tmp.groupby("Month").size())

    elif emp_menu == "➕ Request New Store":
        st.subheader("➕ Add New Store")
        with st.form("store_req"):
            c1,c2 = st.columns(2)
            with c1:
                sname = st.text_input("Store Name*")
                city  = st.text_input("City*")
            with c2:
                gst   = st.text_input("GST Number*", max_chars=15)
                _     = st.text_area("Remarks (optional)", height=100)
            if st.form_submit_button("✅ Add Store", type="primary"):
                gc = gst.strip().upper()
                if not sname or not city or not gc:
                    st.error("❌ All fields required!")
                elif not is_valid_gstin(gc):
                    st.error("❌ Invalid GST! e.g. 22AAAAA0000A1Z5")
                elif safe_col(st.session_state.gst_df,"GSTNumber").astype(str).str.upper().eq(gc).any():
                    st.error("❌ GST exists!")
                else:
                    nid = f"S{len(st.session_state.gst_df)+1:05d}"
                    st.session_state.gst_df = pd.concat([st.session_state.gst_df,
                        pd.DataFrame([{"StoreID":nid,"StoreName":sname.strip().title(),
                                       "GSTNumber":gc,"City":city.strip().title(),"employeecode":emp_code}])
                    ], ignore_index=True)
                    if save_to_supabase("gst_master", st.session_state.gst_df):
                        st.success(f"✅ '{sname.title()}' added!"); st.rerun()

# ====================== FOOTER ======================
st.markdown("---")
st.caption("Beat Plan Pro © 2026 | 🚀 Created By Bipin Pandey")
