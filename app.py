import streamlit as st
import pandas as pd
from datetime import date, timedelta
import re
import io
from supabase import create_client, Client

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="Beat Plan Pro",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== SUPABASE CONFIG ======================
SUPABASE_URL = "https://kueicdruccvbempjvxzn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt1ZWljZHJ1Y2N2YmVtcGp2eHpuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODExMjE0MTcsImV4cCI6MjA5NjY5NzQxN30.aWkQ85Wq-iP2Gp1W1dfoATdRhR0rFcc1H6CGtK_zDE0"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"Failed to connect to Supabase: {e}")
    st.stop()

# ====================== STYLING ======================
st.markdown("""
<style>
    /* ── Base ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: #f8f9fb;
    }

    /* ── Hide default Streamlit chrome ── */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container {
        padding: 1.5rem 2rem 3rem 2rem !important;
        max-width: 1200px !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid #eaecf0 !important;
    }
    [data-testid="stSidebar"] .stRadio > label {
        display: none;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
        gap: 2px !important;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        background: transparent !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 9px 14px !important;
        font-size: 13.5px !important;
        font-weight: 400 !important;
        color: #4b5563 !important;
        cursor: pointer !important;
        transition: background 0.15s !important;
        width: 100% !important;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
        background: #f3f4f6 !important;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-testid="stMarkdownContainer"] p {
        margin: 0 !important;
    }
    /* selected nav item */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) {
        background: #eff6ff !important;
        color: #1d4ed8 !important;
        font-weight: 500 !important;
        border-left: 2px solid #1d4ed8 !important;
        border-radius: 0 8px 8px 0 !important;
    }

    /* ── Topbar brand ── */
    .brand-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 0 1.5rem 0;
        border-bottom: 1px solid #eaecf0;
        margin-bottom: 1.75rem;
    }
    .brand-title {
        font-size: 17px;
        font-weight: 600;
        color: #111827;
        letter-spacing: -0.2px;
    }
    .brand-sub {
        font-size: 12px;
        color: #6b7280;
        margin-top: 1px;
    }
    .user-chip {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 20px;
        padding: 5px 12px 5px 6px;
        font-size: 13px;
        color: #374151;
        font-weight: 500;
    }
    .user-avatar {
        width: 26px;
        height: 26px;
        border-radius: 50%;
        background: #dbeafe;
        color: #1d4ed8;
        font-size: 10px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }

    /* ── Metric cards ── */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 12px;
        margin-bottom: 1.75rem;
    }
    .metric-card {
        background: #ffffff;
        border: 1px solid #eaecf0;
        border-radius: 12px;
        padding: 1.1rem 1.25rem;
    }
    .metric-icon-wrap {
        width: 36px;
        height: 36px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        margin-bottom: 10px;
    }
    .metric-number {
        font-size: 24px;
        font-weight: 600;
        color: #111827;
        line-height: 1;
        margin-bottom: 3px;
    }
    .metric-label {
        font-size: 12px;
        color: #6b7280;
    }
    .metric-trend {
        font-size: 11px;
        margin-top: 8px;
        padding-top: 8px;
        border-top: 1px solid #f3f4f6;
        color: #9ca3af;
    }
    .metric-trend .up { color: #16a34a; font-weight: 500; }

    /* ── Section headers ── */
    .section-header {
        font-size: 15px;
        font-weight: 600;
        color: #111827;
        margin-bottom: 12px;
        margin-top: 1.5rem;
        display: flex;
        align-items: center;
        gap: 7px;
    }
    .section-count {
        font-size: 11px;
        background: #f3f4f6;
        color: #6b7280;
        padding: 2px 7px;
        border-radius: 20px;
        font-weight: 500;
    }

    /* ── Progress bar ── */
    .progress-wrap {
        background: #ffffff;
        border: 1px solid #eaecf0;
        border-radius: 12px;
        padding: 1.1rem 1.25rem;
        margin-bottom: 1.25rem;
    }
    .progress-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .progress-title {
        font-size: 13.5px;
        font-weight: 500;
        color: #111827;
    }
    .progress-fraction {
        font-size: 13px;
        color: #6b7280;
    }
    .progress-fraction strong {
        color: #111827;
        font-weight: 600;
    }
    .bar-bg {
        height: 6px;
        background: #f3f4f6;
        border-radius: 99px;
        overflow: hidden;
    }
    .bar-fill {
        height: 100%;
        border-radius: 99px;
        transition: width 0.3s;
    }
    .bar-blue  { background: #2563eb; }
    .bar-amber { background: #d97706; }
    .bar-red   { background: #dc2626; }
    .progress-note {
        font-size: 11.5px;
        color: #9ca3af;
        margin-top: 6px;
    }

    /* ── Store cards ── */
    .store-card {
        background: #ffffff;
        border: 1px solid #eaecf0;
        border-radius: 12px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 12px;
        transition: border-color 0.15s;
    }
    .store-card:hover { border-color: #d1d5db; }
    .store-avatar {
        width: 40px;
        height: 40px;
        border-radius: 9px;
        background: #eff6ff;
        color: #2563eb;
        font-size: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    .store-info { flex: 1; min-width: 0; }
    .store-name {
        font-size: 13.5px;
        font-weight: 500;
        color: #111827;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .store-meta {
        font-size: 12px;
        color: #6b7280;
        margin-top: 2px;
    }
    .badge {
        font-size: 11px;
        padding: 3px 9px;
        border-radius: 20px;
        font-weight: 500;
        white-space: nowrap;
        flex-shrink: 0;
    }
    .badge-green { background: #dcfce7; color: #15803d; }
    .badge-red   { background: #fee2e2; color: #b91c1c; }
    .badge-blue  { background: #dbeafe; color: #1d4ed8; }
    .badge-gray  { background: #f3f4f6; color: #6b7280; }

    /* ── Upcoming timeline ── */
    .timeline-card {
        background: #ffffff;
        border: 1px solid #eaecf0;
        border-radius: 12px;
        padding: 1.1rem 1.25rem;
        margin-bottom: 8px;
        display: flex;
        gap: 14px;
        align-items: flex-start;
    }
    .date-badge {
        width: 46px;
        flex-shrink: 0;
        text-align: center;
        background: #f9fafb;
        border: 1px solid #eaecf0;
        border-radius: 9px;
        padding: 6px 4px;
    }
    .date-badge.today {
        background: #2563eb;
        border-color: #2563eb;
    }
    .date-day {
        font-size: 20px;
        font-weight: 600;
        color: #111827;
        line-height: 1;
    }
    .date-month {
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #9ca3af;
        margin-top: 2px;
    }
    .date-badge.today .date-day,
    .date-badge.today .date-month { color: #ffffff; }
    .timeline-stores {
        font-size: 13.5px;
        font-weight: 500;
        color: #111827;
        margin-bottom: 2px;
    }
    .timeline-city {
        font-size: 12px;
        color: #6b7280;
        margin-bottom: 6px;
    }
    .pill-row { display: flex; flex-wrap: wrap; gap: 5px; }
    .pill {
        font-size: 11px;
        background: #f3f4f6;
        color: #4b5563;
        padding: 2px 8px;
        border-radius: 20px;
    }

    /* ── Login ── */
    .login-wrap {
        max-width: 400px;
        margin: 3rem auto 0 auto;
    }
    .login-logo {
        text-align: center;
        font-size: 20px;
        font-weight: 600;
        color: #111827;
        margin-bottom: 4px;
    }
    .login-tagline {
        text-align: center;
        font-size: 13px;
        color: #6b7280;
        margin-bottom: 1.75rem;
    }
    .login-card {
        background: #ffffff;
        border: 1px solid #eaecf0;
        border-radius: 14px;
        padding: 1.75rem;
    }

    /* ── Buttons ── */
    .stButton > button {
        border-radius: 8px !important;
        height: 40px !important;
        font-weight: 500 !important;
        font-size: 13.5px !important;
        background: #2563eb !important;
        color: #ffffff !important;
        border: none !important;
        letter-spacing: 0.1px !important;
    }
    .stButton > button:hover {
        background: #1d4ed8 !important;
    }
    .stButton > button[kind="secondary"] {
        background: #f9fafb !important;
        color: #374151 !important;
        border: 1px solid #e5e7eb !important;
    }

    /* ── Inputs ── */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        border-radius: 8px !important;
        border: 1px solid #e5e7eb !important;
        font-size: 13.5px !important;
    }
    .stDateInput > div > div > input {
        border-radius: 8px !important;
        border: 1px solid #e5e7eb !important;
    }

    /* ── Tables ── */
    .stDataFrame {
        border-radius: 12px !important;
        border: 1px solid #eaecf0 !important;
        overflow: hidden !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #f3f4f6;
        border-radius: 9px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 7px;
        font-size: 13px;
        font-weight: 500;
        padding: 6px 16px;
        color: #6b7280;
        background: transparent;
    }
    .stTabs [aria-selected="true"] {
        background: #ffffff !important;
        color: #111827 !important;
        border: 1px solid #e5e7eb !important;
    }

    /* ── Info / warning / success ── */
    .stAlert {
        border-radius: 10px !important;
        font-size: 13.5px !important;
    }

    /* ── Download button ── */
    .stDownloadButton > button {
        background: #f9fafb !important;
        color: #374151 !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }
    .stDownloadButton > button:hover {
        background: #f3f4f6 !important;
    }

    /* ── Divider ── */
    hr { border-color: #eaecf0 !important; margin: 1.5rem 0 !important; }

    /* ── Sidebar brand ── */
    .sidebar-brand {
        padding: 1.25rem 1rem 1rem 1rem;
        border-bottom: 1px solid #eaecf0;
        margin-bottom: 0.75rem;
    }
    .sidebar-brand-title {
        font-size: 15px;
        font-weight: 600;
        color: #111827;
    }
    .sidebar-brand-role {
        font-size: 11px;
        color: #6b7280;
        margin-top: 2px;
    }
    .sidebar-section-label {
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #9ca3af;
        font-weight: 500;
        padding: 0.75rem 1rem 0.25rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ====================== COLUMN NAME NORMALIZER ======================
COLUMN_MAP = {
    "EmployeeCode": ["employeecode", "employee_code"],
    "EmployeeName": ["employeename", "employee_name"],
    "Password":     ["password"],
    "StoreID":      ["storeid", "store_id"],
    "StoreName":    ["storename", "store_name"],
    "GSTNumber":    ["gstnumber", "gst_number"],
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
        st.error(f"Supabase connection failed: {e}")
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
                break
            offset += batch_size
        if all_rows:
            df = pd.DataFrame(all_rows)
            return clean_dataframe(df, columns)
        return pd.DataFrame(columns=columns)
    except Exception as e:
        st.warning(f"Error loading `{table_name}`: {e}")
        return pd.DataFrame(columns=columns)

def sanitize_for_json(df):
    import math
    df_copy = df.copy()
    for col in df_copy.columns:
        if pd.api.types.is_float_dtype(df_copy[col]):
            df_copy[col] = df_copy[col].apply(
                lambda x: None if (x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x)))) else x
            )
        elif df_copy[col].dtype == object:
            df_copy[col] = df_copy[col].apply(
                lambda x: None if (x is None or (isinstance(x, str) and x.lower() in ("nan", "none", ""))) else x
            )
    df_copy = df_copy.where(pd.notnull(df_copy), None)
    return df_copy

def save_to_supabase(table_name, df):
    try:
        df_copy = df.copy()
        if "id" in df_copy.columns:
            df_copy = df_copy.drop("id", axis=1)
        for col in df_copy.columns:
            if col == "VisitDate" or pd.api.types.is_datetime64_any_dtype(df_copy[col]):
                df_copy[col] = pd.to_datetime(df_copy[col], errors="coerce").dt.strftime("%Y-%m-%d")
        df_copy = sanitize_for_json(df_copy)
        try:
            supabase.table(table_name).delete().neq("id", -1).execute()
        except Exception:
            pass
        if not df_copy.empty:
            records = df_copy.to_dict("records")
            records = [{k: v for k, v in rec.items() if v is not None} for rec in records]
            for i in range(0, len(records), 100):
                supabase.table(table_name).insert(records[i:i + 100]).execute()
        return True
    except Exception as e:
        st.error(f"Save failed for `{table_name}`: {e}")
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

def get_bar_class(current, max_val):
    pct = (current / max_val) * 100
    return "bar-red" if pct >= 100 else "bar-amber" if pct >= 80 else "bar-blue"

def safe_col(df, col):
    return df[col] if col in df.columns else pd.Series([""] * len(df))

def get_initials(name):
    parts = str(name).strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper() if len(name) >= 2 else name.upper()

def download_beat_plan_button(df, key, filename_prefix="Beat_Plan"):
    if not df.empty:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Beat Plan")
        output.seek(0)
        st.download_button(
            label="⬇ Download as Excel",
            data=output.getvalue(),
            file_name=f"{filename_prefix}_{date.today().strftime('%Y-%m-%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key=key,
        )

def render_metric(icon, label, value, trend_text=None, icon_bg="#eff6ff", icon_color="#2563eb"):
    trend_html = f"<div class='metric-trend'>{trend_text}</div>" if trend_text else ""
    st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-icon-wrap' style='background:{icon_bg};font-size:16px;color:{icon_color};'>{icon}</div>
            <div class='metric-number'>{value}</div>
            <div class='metric-label'>{label}</div>
            {trend_html}
        </div>""", unsafe_allow_html=True)

def render_topbar(title, subtitle, name=""):
    initials = get_initials(name) if name else ""
    chip_html = f"""
        <div class='user-chip'>
            <div class='user-avatar'>{initials}</div>
            {name}
        </div>""" if name else ""
    st.markdown(f"""
        <div class='brand-bar'>
            <div>
                <div class='brand-title'>{title}</div>
                <div class='brand-sub'>{subtitle}</div>
            </div>
            {chip_html}
        </div>""", unsafe_allow_html=True)

# ====================== LOGIN PAGE ======================
if not st.session_state.logged_in:

    st.markdown("<div class='login-wrap'>", unsafe_allow_html=True)
    st.markdown("""
        <div class='login-logo'>🗺️ Beat Plan Pro</div>
        <div class='login-tagline'>Smart store visit planning system</div>
    """, unsafe_allow_html=True)

    with st.container():
        login_type = st.radio(
            "Login as",
            ["Admin", "Employee"],
            horizontal=True,
            label_visibility="collapsed",
        )

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if login_type == "Admin":
            st.markdown("**Admin login**")
            user = st.text_input("Username", placeholder="Enter username", key="admin_user")
            pwd  = st.text_input("Password", type="password", placeholder="••••••••", key="admin_pwd")
            if st.button("Sign in as Admin", type="primary", use_container_width=True):
                if not user or not pwd:
                    st.error("Please fill in both fields.")
                else:
                    df = st.session_state.admin_df.copy()
                    if "Username" not in df.columns or "Password" not in df.columns:
                        st.error("admin_master columns missing.")
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
                            st.error(f"Invalid credentials. ({len(df)} admin record(s) found)")
        else:
            st.markdown("**Employee login**")
            emp_in = st.text_input("Employee Code", placeholder="e.g. EMP001", key="emp_code_login")
            pwd_in = st.text_input("Password", type="password", placeholder="••••••••", key="emp_pwd_login")
            if st.button("Sign in as Employee", type="primary", use_container_width=True):
                if not emp_in or not pwd_in:
                    st.error("Please fill in both fields.")
                else:
                    df = st.session_state.employee_df.copy()
                    if "EmployeeCode" not in df.columns or "Password" not in df.columns:
                        st.error("employee_master columns missing.")
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
                            st.error(f"Invalid credentials. ({len(df)} employee record(s) found)")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ====================== LOGOUT (sidebar) ======================
with st.sidebar:
    role_label = "Administrator" if st.session_state.role == "admin" else st.session_state.emp_name
    st.markdown(f"""
        <div class='sidebar-brand'>
            <div class='sidebar-brand-title'>🗺️ Beat Plan Pro</div>
            <div class='sidebar-brand-role'>{role_label}</div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("Sign out", use_container_width=True, key="logout_btn"):
        for k, v in {"logged_in": False, "role": "", "emp_code": "", "emp_name": "", "selected_cities": []}.items():
            st.session_state[k] = v
        st.rerun()

# ====================== ADMIN PANEL ======================
if st.session_state.role == "admin":

    with st.sidebar:
        st.markdown("<div class='sidebar-section-label'>Navigation</div>", unsafe_allow_html=True)
        admin_menu = st.radio(
            "nav",
            ["📊  Dashboard", "👥  Employees", "🏪  Stores", "📋  View Plans", "🔄  Refresh"],
            label_visibility="collapsed",
        )

    today_plans = int((st.session_state.planned_df["VisitDate"] == date.today()).sum()) \
        if "VisitDate" in st.session_state.planned_df.columns else 0

    # ── Dashboard ──────────────────────────────────────────
    if "Dashboard" in admin_menu:
        render_topbar(
            "Admin Dashboard",
            f"Overview · {date.today().strftime('%A, %d %B %Y')}",
        )

        cols = st.columns(4)
        metrics = [
            ("👥", "Total employees",  len(st.session_state.employee_df), None,             "#eff6ff", "#2563eb"),
            ("🏪", "Total stores",     len(st.session_state.gst_df),      None,             "#f0fdf4", "#16a34a"),
            ("📋", "Total plans",      len(st.session_state.planned_df),  None,             "#fff7ed", "#d97706"),
            ("📅", "Today's visits",   today_plans,                       None,             "#fdf2f8", "#9333ea"),
        ]
        for col, (icon, label, val, trend, bg, color) in zip(cols, metrics):
            with col:
                render_metric(icon, label, val, trend, bg, color)

        st.markdown("<div class='section-header'>Recent plans</div>", unsafe_allow_html=True)
        if not st.session_state.planned_df.empty:
            st.dataframe(
                st.session_state.planned_df.sort_values("VisitDate", ascending=False).head(10)
                if "VisitDate" in st.session_state.planned_df.columns
                else st.session_state.planned_df.head(10),
                use_container_width=True, hide_index=True,
            )
        else:
            st.info("No plans yet.")

    # ── Employees ──────────────────────────────────────────
    elif "Employees" in admin_menu:
        render_topbar("Employees", "Manage your field team")

        tab1, tab2, tab3 = st.tabs(["  View  ", "  Add  ", "  Delete  "])

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
                    ecode = st.text_input("Employee Code *", placeholder="e.g. EMP042")
                    ename = st.text_input("Employee Name *", placeholder="Full name")
                with c2:
                    epwd  = st.text_input("Password *", type="password", placeholder="Set a password")
                    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                if st.form_submit_button("Add employee", type="primary"):
                    if not ecode or not ename or not epwd:
                        st.error("All fields are required.")
                    elif safe_col(st.session_state.employee_df, "EmployeeCode").astype(str).str.upper().eq(ecode.strip().upper()).any():
                        st.error("That employee code already exists.")
                    else:
                        new_row = pd.DataFrame([{
                            "EmployeeCode": ecode.strip().upper(),
                            "EmployeeName": ename.strip().title(),
                            "Password":     epwd.strip(),
                        }])
                        st.session_state.employee_df = pd.concat(
                            [st.session_state.employee_df, new_row], ignore_index=True
                        )
                        if save_to_supabase("employee_master", st.session_state.employee_df):
                            st.success("Employee added.")
                            st.rerun()

        with tab3:
            if st.session_state.employee_df.empty:
                st.info("No employees.")
            else:
                emp_del = st.selectbox(
                    "Select employee to delete",
                    safe_col(st.session_state.employee_df, "EmployeeCode").unique()
                )
                if st.button("Delete employee", type="primary"):
                    st.session_state.employee_df = st.session_state.employee_df[
                        safe_col(st.session_state.employee_df, "EmployeeCode") != emp_del
                    ]
                    if save_to_supabase("employee_master", st.session_state.employee_df):
                        st.success(f"{emp_del} removed.")
                        st.rerun()

    # ── Stores ─────────────────────────────────────────────
    elif "Stores" in admin_menu:
        render_topbar("Stores", "Manage your store master")

        tab1, tab2, tab3 = st.tabs(["  View  ", "  Add  ", "  Delete  "])

        with tab1:
            if not st.session_state.gst_df.empty:
                st.dataframe(st.session_state.gst_df, use_container_width=True, hide_index=True)
            else:
                st.info("No stores found.")

        with tab2:
            with st.form("add_store"):
                c1, c2 = st.columns(2)
                with c1:
                    sname = st.text_input("Store Name *", placeholder="e.g. Reliance Fresh")
                    gstno = st.text_input("GST Number *", max_chars=15, placeholder="22AAAAA0000A1Z5")
                with c2:
                    city     = st.text_input("City *", placeholder="e.g. Lucknow")
                    emp_opts = safe_col(st.session_state.employee_df, "EmployeeCode").unique().tolist() or ["—"]
                    emp_sel  = st.selectbox("Assign to employee *", emp_opts)
                if st.form_submit_button("Add store", type="primary"):
                    gc = gstno.strip().upper()
                    if not sname or not gc or not city:
                        st.error("All fields are required.")
                    elif not is_valid_gstin(gc):
                        st.error("Invalid GST number. Format: 22AAAAA0000A1Z5")
                    elif safe_col(st.session_state.gst_df, "GSTNumber").astype(str).str.upper().eq(gc).any():
                        st.error("That GST number already exists.")
                    else:
                        nid = f"S{len(st.session_state.gst_df) + 1:05d}"
                        new_store = pd.DataFrame([{
                            "StoreID":      nid,
                            "StoreName":    sname.strip().title(),
                            "GSTNumber":    gc,
                            "City":         city.strip().title(),
                            "EmployeeCode": emp_sel,
                        }])
                        st.session_state.gst_df = pd.concat(
                            [st.session_state.gst_df, new_store], ignore_index=True
                        )
                        if save_to_supabase("gst_master", st.session_state.gst_df):
                            st.success("Store added.")
                            st.rerun()

        with tab3:
            if st.session_state.gst_df.empty:
                st.info("No stores.")
            else:
                sdel = st.selectbox(
                    "Select store to delete",
                    safe_col(st.session_state.gst_df, "StoreID").unique()
                )
                if st.button("Delete store", type="primary"):
                    st.session_state.gst_df = st.session_state.gst_df[
                        safe_col(st.session_state.gst_df, "StoreID") != sdel
                    ]
                    if save_to_supabase("gst_master", st.session_state.gst_df):
                        st.success(f"{sdel} removed.")
                        st.rerun()

    # ── View Plans ─────────────────────────────────────────
    elif "Plans" in admin_menu:
        render_topbar("Visit Plans", "All employee beat plans")

        c1, c2, c3 = st.columns(3)
        with c1:
            femp  = st.selectbox("Employee", ["All"] + list(safe_col(st.session_state.planned_df, "EmployeeName").dropna().unique()))
        with c2:
            fcity = st.selectbox("City",     ["All"] + list(safe_col(st.session_state.planned_df, "City").dropna().unique()))
        with c3:
            drange = st.date_input("Date range", value=(date.today() - timedelta(days=30), date.today()))

        fp = st.session_state.planned_df.copy()
        if femp  != "All" and "EmployeeName" in fp.columns: fp = fp[fp["EmployeeName"] == femp]
        if fcity != "All" and "City"         in fp.columns: fp = fp[fp["City"]          == fcity]
        if isinstance(drange, (list, tuple)) and len(drange) == 2 and "VisitDate" in fp.columns:
            fp = fp[(fp["VisitDate"] >= drange[0]) & (fp["VisitDate"] <= drange[1])]

        st.markdown(
            f"<div class='section-header'>Results <span class='section-count'>{len(fp)}</span></div>",
            unsafe_allow_html=True
        )
        st.dataframe(
            fp.sort_values("VisitDate", ascending=False) if "VisitDate" in fp.columns else fp,
            use_container_width=True, hide_index=True,
        )
        download_beat_plan_button(fp, "admin_dl", "Beat_Plan_Admin")

    # ── Refresh ────────────────────────────────────────────
    elif "Refresh" in admin_menu:
        render_topbar("Refresh Data", "Pull latest records from Supabase")
        st.info("Click below to sync the latest data from all tables.")
        if st.button("Refresh now", type="primary", use_container_width=True):
            st.session_state.employee_df = load_from_supabase("employee_master", EMP_COLS)
            st.session_state.gst_df      = load_from_supabase("gst_master",      GST_COLS)
            st.session_state.planned_df  = load_from_supabase("planned_visits",  PLAN_COLS)
            st.session_state.admin_df    = load_from_supabase("admin_master",    ADMIN_COLS)
            st.success("All data refreshed.")
            st.rerun()

# ====================== EMPLOYEE PANEL ======================
else:
    emp_code = st.session_state.emp_code
    emp_name = st.session_state.emp_name

    with st.sidebar:
        st.markdown("<div class='sidebar-section-label'>Navigation</div>", unsafe_allow_html=True)
        emp_menu = st.radio(
            "nav",
            ["🎯  New Beat Plan", "📅  My Plans", "📆  Upcoming", "📊  Analytics", "➕  Add Store"],
            label_visibility="collapsed",
        )

    employee_stores = st.session_state.gst_df[
        safe_col(st.session_state.gst_df, "EmployeeCode").astype(str) == str(emp_code)
    ] if not st.session_state.gst_df.empty else pd.DataFrame(columns=GST_COLS)

    # ── New Beat Plan ───────────────────────────────────────
    if "New Beat Plan" in emp_menu:
        render_topbar("New Beat Plan", f"Plan your store visits", name=emp_name)

        if employee_stores.empty:
            st.warning("No stores are assigned to you yet. Contact your admin.")
            st.stop()

        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            visit_date = st.date_input("Visit date", value=date.today(), key="beat_date")
        with c2:
            city_opts  = sorted(safe_col(employee_stores, "City").dropna().unique().tolist())
            sel_cities = st.multiselect("Filter cities (up to 3)", city_opts, max_selections=3, key="city_ms")
        with c3:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            if st.button("Load stores", use_container_width=True):
                st.session_state.selected_cities = sel_cities

        # Daily progress
        daily_plans = st.session_state.planned_df[
            (safe_col(st.session_state.planned_df, "EmployeeCode").astype(str) == str(emp_code)) &
            (st.session_state.planned_df["VisitDate"] == visit_date)
        ] if "VisitDate" in st.session_state.planned_df.columns else pd.DataFrame(columns=PLAN_COLS)

        pc        = len(daily_plans)
        bar_class = get_bar_class(pc, 10)
        bar_pct   = min(pc * 10, 100)
        note      = "Daily limit of 10 reached." if pc >= 10 else f"{10 - pc} more store(s) can be added today."

        st.markdown(f"""
            <div class='progress-wrap'>
                <div class='progress-row'>
                    <span class='progress-title'>Today's progress</span>
                    <span class='progress-fraction'><strong>{pc}</strong> / 10 stores</span>
                </div>
                <div class='bar-bg'>
                    <div class='bar-fill {bar_class}' style='width:{bar_pct}%'></div>
                </div>
                <div class='progress-note'>{note}</div>
            </div>""", unsafe_allow_html=True)

        if not daily_plans.empty:
            with st.expander(f"Already planned for {visit_date} — {pc} store(s)"):
                show = [c for c in ["Store", "City", "GSTNumber"] if c in daily_plans.columns]
                st.dataframe(daily_plans[show], use_container_width=True, hide_index=True)

        if pc < 10:
            show_cities = st.session_state.selected_cities or safe_col(employee_stores, "City").unique().tolist()
            city_stores = employee_stores[safe_col(employee_stores, "City").isin(show_cities)]
            planned_ids = safe_col(daily_plans, "StoreID").tolist()
            available   = city_stores[~safe_col(city_stores, "StoreID").isin(planned_ids)]

            st.markdown(
                f"<div class='section-header'>Available stores <span class='section-count'>{len(available)}</span></div>",
                unsafe_allow_html=True
            )

            if available.empty:
                st.info("No more stores available for the selected cities.")
            else:
                for idx, row in available.iterrows():
                    col1, col2 = st.columns([6, 1])
                    with col1:
                        st.markdown(f"""
                            <div class='store-card'>
                                <div class='store-avatar'>🏪</div>
                                <div class='store-info'>
                                    <div class='store-name'>{row.get('StoreName', '—')}</div>
                                    <div class='store-meta'>
                                        {row.get('StoreID', '—')} &nbsp;·&nbsp;
                                        {row.get('City', '—')} &nbsp;·&nbsp;
                                        GST: {row.get('GSTNumber', '—')}
                                    </div>
                                </div>
                                <span class='badge badge-green'>Available</span>
                            </div>""", unsafe_allow_html=True)
                    with col2:
                        st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
                        if st.button("+ Add", key=f"add_{idx}_{visit_date}"):
                            new_plan = pd.DataFrame([{
                                "EmployeeCode": emp_code,
                                "EmployeeName": emp_name,
                                "City":         row.get("City", ""),
                                "Store":        row.get("StoreName", ""),
                                "StoreID":      row.get("StoreID", ""),
                                "GSTNumber":    row.get("GSTNumber", ""),
                                "VisitDate":    visit_date,
                            }])
                            st.session_state.planned_df = pd.concat(
                                [st.session_state.planned_df, new_plan], ignore_index=True
                            )
                            if save_to_supabase("planned_visits", st.session_state.planned_df):
                                st.success(f"{row.get('StoreName', '')} added to your plan.")
                                st.rerun()

        st.markdown("---")
        emp_plans = st.session_state.planned_df[
            safe_col(st.session_state.planned_df, "EmployeeCode").astype(str) == str(emp_code)
        ]
        download_beat_plan_button(emp_plans, "emp_dl", f"Beat_Plan_{emp_code}")

    # ── My Plans ───────────────────────────────────────────
    elif "My Plans" in emp_menu:
        render_topbar("My Plans", "All your scheduled visits", name=emp_name)

        my = st.session_state.planned_df[
            safe_col(st.session_state.planned_df, "EmployeeCode").astype(str) == str(emp_code)
        ]
        if my.empty:
            st.info("You haven't created any plans yet.")
        else:
            c1, c2, c3 = st.columns(3)
            with c1:
                render_metric("📋", "Total plans",   len(my),                                   None, "#eff6ff", "#2563eb")
            with c2:
                render_metric("🌍", "Cities covered", safe_col(my, "City").nunique(),            None, "#f0fdf4", "#16a34a")
            with c3:
                render_metric("📅", "Unique dates",   len(safe_col(my, "VisitDate").unique()),   None, "#fff7ed", "#d97706")

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            st.dataframe(
                my.sort_values("VisitDate", ascending=False) if "VisitDate" in my.columns else my,
                use_container_width=True, hide_index=True,
            )
            download_beat_plan_button(my, "my_dl", f"My_Plans_{emp_code}")

    # ── Upcoming ───────────────────────────────────────────
    elif "Upcoming" in emp_menu:
        render_topbar("Upcoming Visits", "Your planned schedule ahead", name=emp_name)

        if "VisitDate" not in st.session_state.planned_df.columns:
            st.info("No upcoming visits.")
        else:
            upcoming = st.session_state.planned_df[
                (safe_col(st.session_state.planned_df, "EmployeeCode").astype(str) == str(emp_code)) &
                (st.session_state.planned_df["VisitDate"] >= date.today())
            ].sort_values("VisitDate")

            if upcoming.empty:
                st.info("No upcoming visits scheduled.")
            else:
                for vdate in sorted(upcoming["VisitDate"].unique()):
                    plans      = upcoming[upcoming["VisitDate"] == vdate]
                    is_today   = vdate == date.today()
                    badge_cls  = "date-badge today" if is_today else "date-badge"
                    day_num    = vdate.strftime("%d")
                    month_str  = vdate.strftime("%b")
                    cities     = ", ".join(sorted(safe_col(plans, "City").dropna().unique().tolist()))
                    store_names = safe_col(plans, "Store").dropna().unique().tolist()
                    pills_html  = "".join(
                        f"<span class='pill'>{s}</span>"
                        for s in store_names[:4]
                    )
                    if len(store_names) > 4:
                        pills_html += f"<span class='pill'>+{len(store_names)-4} more</span>"

                    st.markdown(f"""
                        <div class='timeline-card'>
                            <div class='{badge_cls}'>
                                <div class='date-day'>{day_num}</div>
                                <div class='date-month'>{month_str}</div>
                            </div>
                            <div>
                                <div class='timeline-stores'>{len(plans)} store(s) planned</div>
                                <div class='timeline-city'>{cities}</div>
                                <div class='pill-row'>{pills_html}</div>
                            </div>
                        </div>""", unsafe_allow_html=True)

    # ── Analytics ──────────────────────────────────────────
    elif "Analytics" in emp_menu:
        render_topbar("Analytics", "Your performance at a glance", name=emp_name)

        my = st.session_state.planned_df[
            safe_col(st.session_state.planned_df, "EmployeeCode").astype(str) == str(emp_code)
        ]
        if my.empty:
            st.info("No data to display yet.")
        else:
            tm = my[pd.to_datetime(safe_col(my, "VisitDate"), errors="coerce").dt.month == date.today().month] \
                if "VisitDate" in my.columns else pd.DataFrame()

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                render_metric("📋", "Total visits",  len(my),                             None, "#eff6ff", "#2563eb")
            with c2:
                render_metric("🌍", "Cities",         safe_col(my, "City").nunique(),     None, "#f0fdf4", "#16a34a")
            with c3:
                render_metric("🏪", "Unique stores",  safe_col(my, "Store").nunique(),    None, "#fff7ed", "#d97706")
            with c4:
                render_metric("📅", "This month",     len(tm),                             None, "#fdf2f8", "#9333ea")

            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("<div class='section-header'>Visits by city</div>", unsafe_allow_html=True)
                if "City" in my.columns:
                    st.bar_chart(my.groupby("City").size(), color="#2563eb")
            with c2:
                st.markdown("<div class='section-header'>Visits over time</div>", unsafe_allow_html=True)
                if "VisitDate" in my.columns:
                    tmp = my.copy()
                    tmp["Month"] = pd.to_datetime(tmp["VisitDate"], errors="coerce").dt.to_period("M").astype(str)
                    st.line_chart(tmp.groupby("Month").size(), color="#16a34a")

    # ── Add Store ──────────────────────────────────────────
    elif "Add Store" in emp_menu:
        render_topbar("Add New Store", "Request a store to be added to your territory", name=emp_name)

        with st.form("store_req"):
            c1, c2 = st.columns(2)
            with c1:
                sname = st.text_input("Store Name *", placeholder="e.g. Big Bazaar")
                city  = st.text_input("City *",       placeholder="e.g. Lucknow")
            with c2:
                gst = st.text_input("GST Number *", max_chars=15, placeholder="22AAAAA0000A1Z5")
                st.text_area("Remarks (optional)", height=100, placeholder="Any notes for admin...")
            if st.form_submit_button("Add store", type="primary"):
                gc = gst.strip().upper()
                if not sname or not city or not gc:
                    st.error("All fields are required.")
                elif not is_valid_gstin(gc):
                    st.error("Invalid GST number. Format: 22AAAAA0000A1Z5")
                elif safe_col(st.session_state.gst_df, "GSTNumber").astype(str).str.upper().eq(gc).any():
                    st.error("That GST number already exists in the system.")
                else:
                    nid = f"S{len(st.session_state.gst_df) + 1:05d}"
                    new_store = pd.DataFrame([{
                        "StoreID":      nid,
                        "StoreName":    sname.strip().title(),
                        "GSTNumber":    gc,
                        "City":         city.strip().title(),
                        "EmployeeCode": emp_code,
                    }])
                    st.session_state.gst_df = pd.concat(
                        [st.session_state.gst_df, new_store], ignore_index=True
                    )
                    if save_to_supabase("gst_master", st.session_state.gst_df):
                        st.success(f"'{sname.title()}' has been added to your territory.")
                        st.rerun()

# ====================== FOOTER ======================
st.markdown("---")
st.caption("Beat Plan Pro · 2026 · Built by Bipin Pandey")
