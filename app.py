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
    initial_sidebar_state="collapsed"
)

# ====================== SUPABASE CONFIG ======================
SUPABASE_URL = "https://kueicdruccvbempjvxzn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt1ZWljZHJ1Y2N2YmVtcGp2eHpuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODExMjE0MTcsImV4cCI6MjA5NjY5NzQxN30.aWkQ85Wq-iP2Gp1W1dfoATdRhR0rFcc1H6CGtK_zDE0"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"Failed to connect to Supabase: {e}")
    st.stop()

# ====================== CSS ======================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

.stApp { background: #f0f2f5 !important; }
.block-container { padding: 1.5rem 2rem 4rem 2rem !important; max-width: 1100px !important; }
#MainMenu, footer, header { visibility: hidden; }

/* ── Hide sidebar toggle ── */
[data-testid="collapsedControl"] { display: none !important; }

/* ── TOP NAV BAR ── */
.topnav {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 12px 20px;
    display: flex;
    align-items: center;
    gap: 0;
    margin-bottom: 1.5rem;
}
.topnav-logo {
    display: flex; align-items: center; gap: 8px;
    font-size: 15px; font-weight: 700; color: #111827;
    margin-right: 24px; white-space: nowrap;
}
.logo-dots { display: flex; flex-direction: column; gap: 3px; }
.logo-dot1 { width: 8px; height: 8px; background: #4f46e5; border-radius: 50%; }
.logo-dot2 { width: 5px; height: 5px; background: #06b6d4; border-radius: 50%; margin-left: 1px; }
.topnav-links { display: flex; gap: 6px; flex: 1; }
.topnav-btn {
    padding: 7px 18px; border-radius: 10px;
    font-size: 13.5px; font-weight: 500; cursor: pointer;
    border: 1px solid #e5e7eb; background: #ffffff; color: #374151;
    transition: all 0.15s;
}
.topnav-btn:hover { background: #f9fafb; }
.topnav-btn.active { background: #4f46e5; color: #ffffff; border-color: #4f46e5; }
.topnav-user {
    display: flex; align-items: center; gap: 9px;
    font-size: 13.5px; font-weight: 600; color: #374151;
    margin-left: auto;
}
.topnav-avatar {
    width: 34px; height: 34px; border-radius: 50%;
    background: linear-gradient(135deg, #4f46e5, #06b6d4);
    color: #fff; font-size: 12px; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
}

/* ── STAT CARDS ── */
.stats-row {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 14px;
    margin-bottom: 1.5rem;
}
.stat-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
}
.stat-left-bar {
    position: absolute; top: 0; left: 0;
    width: 4px; height: 100%;
    border-radius: 16px 0 0 16px;
}
.stat-icon-wrap {
    width: 36px; height: 36px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 14px; font-size: 17px;
}
.stat-number {
    font-size: 28px; font-weight: 700; color: #111827;
    letter-spacing: -0.5px; line-height: 1; margin-bottom: 4px;
}
.stat-label { font-size: 12.5px; color: #9ca3af; font-weight: 500; }
.stat-trend {
    font-size: 12px; font-weight: 600; margin-top: 10px;
    padding-top: 10px; border-top: 1px solid #f3f4f6;
}

/* ── TWO COLUMN CONTENT ── */
.content-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    margin-bottom: 14px;
}

/* ── PANEL CARD ── */
.panel-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 20px 22px;
}
.panel-header {
    display: flex; align-items: center; gap: 8px;
    font-size: 14px; font-weight: 700; color: #374151;
    margin-bottom: 14px;
    padding-bottom: 12px;
    border-bottom: 1px solid #f3f4f6;
}
.panel-badge {
    font-size: 11px; padding: 2px 9px;
    border-radius: 20px; font-weight: 600;
    background: #eef2ff; color: #4338ca;
    margin-left: auto;
}
.panel-icon { font-size: 16px; }

/* ── PROGRESS BAR ── */
.prog-row {
    display: flex; justify-content: space-between;
    align-items: center; margin-bottom: 8px;
}
.prog-label { font-size: 13px; font-weight: 500; color: #374151; }
.prog-count { font-size: 13px; color: #9ca3af; font-weight: 600; }
.prog-bg { height: 7px; background: #f3f4f6; border-radius: 99px; overflow: hidden; margin-bottom: 16px; }
.prog-fill { height: 100%; border-radius: 99px; }

/* ── STORE ITEM ── */
.store-item {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid #f9fafb;
}
.store-item:last-child { border-bottom: none; }
.store-icon-wrap {
    width: 36px; height: 36px; border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 15px; flex-shrink: 0;
}
.si-blue   { background: #eef2ff; color: #4f46e5; }
.si-red    { background: #fef2f2; color: #dc2626; }
.si-amber  { background: #fffbeb; color: #d97706; }
.store-name-txt { font-size: 13.5px; font-weight: 600; color: #111827; }
.store-meta-txt { font-size: 12px; color: #9ca3af; margin-top: 1px; }

/* ── BADGE ── */
.badge {
    font-size: 11px; padding: 3px 10px; border-radius: 20px;
    font-weight: 600; white-space: nowrap; flex-shrink: 0;
}
.badge-green  { background: #dcfce7; color: #15803d; }
.badge-red    { background: #fee2e2; color: #b91c1c; }
.badge-amber  { background: #fef9c3; color: #854d0e; }

/* ── TIMELINE ── */
.timeline-item {
    display: flex; gap: 14px; align-items: flex-start;
    padding: 10px 0; border-bottom: 1px solid #f9fafb;
}
.timeline-item:last-child { border-bottom: none; padding-bottom: 0; }
.t-date-badge {
    width: 46px; flex-shrink: 0; text-align: center;
    border-radius: 12px; padding: 8px 5px;
}
.t-date-badge.today { background: #4f46e5; }
.t-date-badge.future { background: #f3f4f6; border: 1px solid #e5e7eb; }
.t-day { font-size: 20px; font-weight: 700; line-height: 1; }
.t-mon { font-size: 10px; text-transform: uppercase; letter-spacing: .05em; margin-top: 2px; }
.t-date-badge.today .t-day, .t-date-badge.today .t-mon { color: #ffffff; }
.t-date-badge.future .t-day { color: #111827; }
.t-date-badge.future .t-mon { color: #9ca3af; }
.t-stores-lbl { font-size: 13.5px; font-weight: 600; color: #111827; margin-bottom: 2px; }
.t-city-lbl   { font-size: 12px; color: #9ca3af; margin-bottom: 6px; }
.t-pills      { display: flex; flex-wrap: wrap; gap: 4px; }
.t-pill       { font-size: 11px; background: #f3f4f6; color: #4b5563; padding: 2px 8px; border-radius: 20px; }

/* ── SECTION HEADING ── */
.sec-head {
    font-size: 14px; font-weight: 700; color: #374151;
    margin: 1.5rem 0 10px 0;
    display: flex; align-items: center; gap: 8px;
}
.sec-cnt {
    font-size: 11px; background: #f3f4f6; color: #6b7280;
    padding: 2px 8px; border-radius: 20px; font-weight: 500;
}

/* ── LOGIN ── */
.login-wrap { max-width: 420px; margin: 2rem auto 0; }
.login-logo-box {
    text-align: center; margin-bottom: 1.75rem;
}
.login-icon {
    width: 54px; height: 54px; border-radius: 14px;
    background: linear-gradient(135deg, #4f46e5, #06b6d4);
    display: inline-flex; align-items: center;
    justify-content: center; font-size: 24px; color: #fff;
    margin-bottom: 12px;
}
.login-title { font-size: 22px; font-weight: 700; color: #111827; }
.login-sub   { font-size: 13px; color: #9ca3af; margin-top: 4px; }
.login-card  {
    background: #fff; border: 1px solid #e5e7eb;
    border-radius: 18px; padding: 28px 30px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.04);
}

/* ── BUTTONS ── */
.stButton > button {
    border-radius: 10px !important; height: 42px !important;
    font-weight: 600 !important; font-size: 13.5px !important;
    background: #4f46e5 !important; color: #fff !important;
    border: none !important; letter-spacing: 0.1px !important;
}
.stButton > button:hover { background: #4338ca !important; }

/* ── INPUTS ── */
.stTextInput > div > div > input {
    border-radius: 10px !important; border: 1.5px solid #e5e7eb !important;
    font-size: 13.5px !important; background: #fafafa !important;
}
.stTextInput > div > div > input:focus {
    border-color: #4f46e5 !important; background: #fff !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,0.08) !important;
}
.stSelectbox > div > div {
    border-radius: 10px !important; border: 1.5px solid #e5e7eb !important;
}
.stMultiSelect > div > div {
    border-radius: 10px !important; border: 1.5px solid #e5e7eb !important;
}
.stDateInput > div > div > input {
    border-radius: 10px !important; border: 1.5px solid #e5e7eb !important;
}
.stTextArea > div > div > textarea {
    border-radius: 10px !important; border: 1.5px solid #e5e7eb !important;
    font-size: 13.5px !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 3px; background: #f0f2f5;
    border-radius: 12px; padding: 4px; border: none !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px !important; font-size: 13px !important;
    font-weight: 500 !important; padding: 7px 20px !important;
    color: #6b7280 !important; background: transparent !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: #ffffff !important; color: #111827 !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07) !important;
}

/* ── TABLE ── */
.stDataFrame {
    border-radius: 14px !important; border: 1px solid #e5e7eb !important;
    overflow: hidden !important;
}

/* ── ALERTS ── */
.stAlert { border-radius: 12px !important; font-size: 13.5px !important; }

/* ── DOWNLOAD ── */
.stDownloadButton > button {
    background: #f9fafb !important; color: #374151 !important;
    border: 1.5px solid #e5e7eb !important;
    border-radius: 10px !important; font-weight: 600 !important;
}

/* ── EXPANDER ── */
.streamlit-expanderHeader {
    background: #f9fafb !important; border-radius: 10px !important;
    font-size: 13.5px !important; font-weight: 600 !important;
    border: 1px solid #e5e7eb !important;
}

/* ── DIVIDER ── */
hr { border-color: #e5e7eb !important; margin: 1.5rem 0 !important; }

/* ── SIDEBAR (used only for admin extra nav) ── */
[data-testid="stSidebar"] { background: #ffffff !important; border-right: 1px solid #e5e7eb !important; }
[data-testid="stSidebar"] .stRadio > label { display: none; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] { gap: 1px !important; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    background: transparent !important; border: none !important;
    border-left: 2.5px solid transparent !important; border-radius: 0 !important;
    padding: 10px 16px !important; font-size: 13.5px !important;
    font-weight: 400 !important; color: #6b7280 !important;
    cursor: pointer !important; width: 100% !important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) {
    background: #eef2ff !important; color: #4f46e5 !important;
    border-left-color: #4f46e5 !important; font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)

# ====================== COLUMN MAP ======================
COLUMN_MAP = {
    "EmployeeCode": ["employeecode","employee_code"],
    "EmployeeName": ["employeename","employee_name"],
    "Password":     ["password"],
    "StoreID":      ["storeid","store_id"],
    "StoreName":    ["storename","store_name"],
    "GSTNumber":    ["gstnumber","gst_number"],
    "City":         ["city"],
    "Store":        ["store"],
    "VisitDate":    ["visitdate","visit_date"],
    "Username":     ["username"],
}

def normalize_columns(df):
    rename = {}
    lower_map = {c.lower().replace("_",""): c for c in df.columns}
    for expected, variants in COLUMN_MAP.items():
        if expected in df.columns: continue
        for v in variants:
            key = v.lower().replace("_","")
            if key in lower_map:
                rename[lower_map[key]] = expected
                break
    return df.rename(columns=rename) if rename else df

# ====================== DB ======================
def init_db():
    try:
        supabase.table("planned_visits").select("*").limit(1).execute()
        return True
    except Exception as e:
        st.error(f"Supabase connection failed: {e}")
        return False

def clean_dataframe(df, expected_columns):
    if df.empty: return df
    df = normalize_columns(df)
    for col in expected_columns:
        if col not in df.columns: df[col] = ""
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()
    if "VisitDate" in df.columns:
        df["VisitDate"] = pd.to_datetime(df["VisitDate"], errors="coerce").dt.date
    return df

def load_from_supabase(table_name, columns):
    try:
        all_rows, batch_size, offset = [], 1000, 0
        while True:
            response = supabase.table(table_name).select("*").range(offset, offset+batch_size-1).execute()
            if not response.data: break
            all_rows.extend(response.data)
            if len(response.data) < batch_size: break
            offset += batch_size
        if all_rows:
            return clean_dataframe(pd.DataFrame(all_rows), columns)
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
                lambda x: None if (x is None or (isinstance(x,float) and (math.isnan(x) or math.isinf(x)))) else x)
        elif df_copy[col].dtype == object:
            df_copy[col] = df_copy[col].apply(
                lambda x: None if (x is None or (isinstance(x,str) and x.lower() in ("nan","none",""))) else x)
    return df_copy.where(pd.notnull(df_copy), None)

def save_to_supabase(table_name, df):
    try:
        df_copy = df.copy()
        if "id" in df_copy.columns: df_copy = df_copy.drop("id", axis=1)
        for col in df_copy.columns:
            if col == "VisitDate" or pd.api.types.is_datetime64_any_dtype(df_copy[col]):
                df_copy[col] = pd.to_datetime(df_copy[col], errors="coerce").dt.strftime("%Y-%m-%d")
        df_copy = sanitize_for_json(df_copy)
        try: supabase.table(table_name).delete().neq("id",-1).execute()
        except: pass
        if not df_copy.empty:
            records = [{k:v for k,v in r.items() if v is not None} for r in df_copy.to_dict("records")]
            for i in range(0, len(records), 100):
                supabase.table(table_name).insert(records[i:i+100]).execute()
        return True
    except Exception as e:
        st.error(f"Save failed for `{table_name}`: {e}")
        return False

# ====================== CONSTANTS ======================
EMP_COLS   = ["EmployeeCode","EmployeeName","Password"]
GST_COLS   = ["StoreID","StoreName","GSTNumber","City","EmployeeCode"]
PLAN_COLS  = ["EmployeeCode","EmployeeName","City","Store","GSTNumber","StoreID","VisitDate"]
ADMIN_COLS = ["Username","Password"]

# ====================== INIT ======================
if not init_db(): st.stop()

for key, loader in [
    ("employee_df", lambda: load_from_supabase("employee_master", EMP_COLS)),
    ("gst_df",      lambda: load_from_supabase("gst_master",      GST_COLS)),
    ("planned_df",  lambda: load_from_supabase("planned_visits",  PLAN_COLS)),
    ("admin_df",    lambda: load_from_supabase("admin_master",    ADMIN_COLS)),
]:
    if key not in st.session_state: st.session_state[key] = loader()

for k,v in {"logged_in":False,"role":"","emp_code":"","emp_name":"","page":"Dashboard","selected_cities":[]}.items():
    if k not in st.session_state: st.session_state[k] = v

# ====================== HELPERS ======================
def is_valid_gstin(g):
    return bool(re.match(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$", str(g).strip().upper()))

def safe_col(df, col):
    return df[col] if col in df.columns else pd.Series([""]*len(df))

def get_initials(name):
    parts = str(name).strip().split()
    return (parts[0][0]+parts[-1][0]).upper() if len(parts)>=2 else name[:2].upper()

def get_prog_color(pc):
    return "#4f46e5" if pc < 8 else "#f59e0b" if pc < 10 else "#ef4444"

def download_button(df, key, prefix="Beat_Plan"):
    if not df.empty:
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine="openpyxl") as w:
            df.to_excel(w, index=False, sheet_name="Beat Plan")
        out.seek(0)
        st.download_button("⬇  Download Excel", data=out.getvalue(),
            file_name=f"{prefix}_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True, key=key)

def render_topnav(name, role, page):
    """Render the top navigation bar matching screenshot exactly."""
    initials = get_initials(name) if name else ("AD" if role=="admin" else "??")

    # Build nav buttons based on role
    if role == "admin":
        nav_items = ["Dashboard","Employees","Stores","View Plans","Refresh"]
    else:
        nav_items = ["Dashboard","Beat Plan","My Plans","Analytics"]

    # Extra pages for employee that aren't in top nav go via a More button
    btns_html = ""
    for item in nav_items:
        active = "active" if page == item else ""
        btns_html += f'<button class="topnav-btn {active}" onclick="void(0)">{item}</button>'

    st.markdown(f"""
    <div class="topnav">
        <div class="topnav-logo">
            <div class="logo-dots">
                <div class="logo-dot1"></div>
                <div class="logo-dot2"></div>
            </div>
            Beat Plan Pro
        </div>
        <div class="topnav-links">
            {btns_html}
        </div>
        <div class="topnav-user">
            <div class="topnav-avatar">{initials}</div>
            {name}
        </div>
    </div>""", unsafe_allow_html=True)

def render_stat_cards(stats):
    """stats = list of (accent, icon_bg, icon_color, emoji, value, label, trend, trend_color)"""
    html = "<div class='stats-row'>"
    for accent, icon_bg, icon_color, emoji, value, label, trend, tcolor in stats:
        html += f"""
        <div class="stat-card">
            <div class="stat-left-bar" style="background:{accent}"></div>
            <div class="stat-icon-wrap" style="background:{icon_bg};color:{icon_color};">{emoji}</div>
            <div class="stat-number">{value}</div>
            <div class="stat-label">{label}</div>
            <div class="stat-trend" style="color:{tcolor};">{trend}</div>
        </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

# ====================== LOGIN ======================
if not st.session_state.logged_in:
    st.markdown("<div class='login-wrap'>", unsafe_allow_html=True)
    st.markdown("""
        <div class="login-logo-box">
            <div class="login-icon">🗺️</div>
            <div class="login-title">Beat Plan Pro</div>
            <div class="login-sub">Smart store visit planning system</div>
        </div>
    """, unsafe_allow_html=True)

    with st.container():
        login_type = st.radio("Login as", ["👤  Admin", "👷  Employee"], horizontal=True, label_visibility="collapsed")
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        if "Admin" in login_type:
            user = st.text_input("Username", placeholder="Enter your username", key="admin_user")
            pwd  = st.text_input("Password", type="password", placeholder="••••••••", key="admin_pwd")
            if st.button("Sign in as Admin", type="primary", use_container_width=True):
                if not user or not pwd:
                    st.error("Please fill in both fields.")
                else:
                    df = st.session_state.admin_df
                    match = (
                        (df["Username"].astype(str).str.strip() == user.strip()) &
                        (df["Password"].astype(str).str.strip() == pwd.strip())
                    ) if "Username" in df.columns else pd.Series([False])
                    if match.any():
                        st.session_state.logged_in = True
                        st.session_state.role = "admin"
                        st.session_state.emp_name = "Admin"
                        st.session_state.page = "Dashboard"
                        st.rerun()
                    else:
                        st.error(f"Invalid credentials. ({len(df)} admin record(s) found)")
        else:
            emp_in = st.text_input("Employee Code", placeholder="e.g. EMP001", key="emp_code_login")
            pwd_in = st.text_input("Password", type="password", placeholder="••••••••", key="emp_pwd_login")
            if st.button("Sign in as Employee", type="primary", use_container_width=True):
                if not emp_in or not pwd_in:
                    st.error("Please fill in both fields.")
                else:
                    df = st.session_state.employee_df
                    match = df[
                        (df["EmployeeCode"].astype(str).str.strip() == emp_in.strip()) &
                        (df["Password"].astype(str).str.strip()     == pwd_in.strip())
                    ] if "EmployeeCode" in df.columns else pd.DataFrame()
                    if not match.empty:
                        st.session_state.logged_in = True
                        st.session_state.role      = "employee"
                        st.session_state.emp_code  = str(match.iloc[0]["EmployeeCode"])
                        st.session_state.emp_name  = match.iloc[0]["EmployeeName"]
                        st.session_state.page      = "Dashboard"
                        st.rerun()
                    else:
                        st.error(f"Invalid credentials. ({len(df)} employee record(s) found)")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ====================== MAIN APP ======================
role     = st.session_state.role
emp_code = st.session_state.emp_code
emp_name = st.session_state.emp_name
page     = st.session_state.page

# ── Top nav rendering + page switcher ──────────────────────────
render_topnav(emp_name, role, page)

# Top nav page switching (using st.columns with invisible buttons mapped to pages)
if role == "admin":
    nav_pages = ["Dashboard","Employees","Stores","View Plans","Refresh"]
else:
    nav_pages = ["Dashboard","Beat Plan","My Plans","Analytics"]

cols_nav = st.columns(len(nav_pages) + 3)
for i, p in enumerate(nav_pages):
    with cols_nav[i]:
        if st.button(p, key=f"nav_{p}", use_container_width=True):
            st.session_state.page = p
            st.rerun()

# Extra employee pages via sidebar-style selectbox (hidden but accessible)
if role == "employee":
    with st.sidebar:
        extra = st.radio("Extra", ["➕ Add Store","📆 Upcoming"], label_visibility="collapsed")
        if st.button("Go", key="go_extra"):
            st.session_state.page = extra.split(" ",1)[1].strip()
            st.rerun()
        if st.button("🚪 Sign out", use_container_width=True, key="logout_side"):
            for k,v in {"logged_in":False,"role":"","emp_code":"","emp_name":"","page":"Dashboard","selected_cities":[]}.items():
                st.session_state[k] = v
            st.rerun()
else:
    with st.sidebar:
        if st.button("🚪 Sign out", use_container_width=True, key="logout_side"):
            for k,v in {"logged_in":False,"role":"","emp_code":"","emp_name":"","page":"Dashboard","selected_cities":[]}.items():
                st.session_state[k] = v
            st.rerun()

# Re-read page after potential rerun
page = st.session_state.page

# ====================== ADMIN PAGES ======================
if role == "admin":

    today_plans = int((st.session_state.planned_df["VisitDate"] == date.today()).sum()) \
        if "VisitDate" in st.session_state.planned_df.columns else 0

    # ── DASHBOARD ─────────────────────────────────────────────────
    if page == "Dashboard":
        render_stat_cards([
            ("#4f46e5","#eef2ff","#4f46e5","👥", len(st.session_state.employee_df), "Total employees", "↑ 3 this month",  "#10b981"),
            ("#06b6d4","#ecfeff","#0891b2","🏪", len(st.session_state.gst_df),      "Total stores",    "↑ 8 new stores",  "#10b981"),
            ("#f59e0b","#fffbeb","#d97706","📋", len(st.session_state.planned_df),  "Total plans",     "↑ 47 this week",  "#10b981"),
            ("#10b981","#d1fae5","#059669","📍", today_plans,                        "Today's visits",  "Across cities",   "#9ca3af"),
        ])
        st.markdown("<div class='sec-head'>Recent plans</div>", unsafe_allow_html=True)
        df_show = st.session_state.planned_df.sort_values("VisitDate",ascending=False).head(10) \
            if "VisitDate" in st.session_state.planned_df.columns else st.session_state.planned_df.head(10)
        st.dataframe(df_show, use_container_width=True, hide_index=True) if not df_show.empty else st.info("No plans yet.")

    # ── EMPLOYEES ─────────────────────────────────────────────────
    elif page == "Employees":
        st.markdown("<div class='sec-head'>👥 Employees</div>", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["  View  ","  Add  ","  Delete  "])
        with tab1:
            disp = st.session_state.employee_df.drop(columns=["Password"], errors="ignore")
            st.dataframe(disp, use_container_width=True, hide_index=True) if not disp.empty else st.info("No employees found.")
        with tab2:
            with st.form("add_emp"):
                c1,c2 = st.columns(2)
                with c1:
                    ecode = st.text_input("Employee Code *", placeholder="e.g. EMP042")
                    ename = st.text_input("Employee Name *", placeholder="Full name")
                with c2:
                    epwd = st.text_input("Password *", type="password", placeholder="Set a password")
                    st.markdown("<div style='height:27px'></div>", unsafe_allow_html=True)
                if st.form_submit_button("Add employee", type="primary"):
                    if not ecode or not ename or not epwd:
                        st.error("All fields are required.")
                    elif safe_col(st.session_state.employee_df,"EmployeeCode").astype(str).str.upper().eq(ecode.strip().upper()).any():
                        st.error("That employee code already exists.")
                    else:
                        new_row = pd.DataFrame([{"EmployeeCode":ecode.strip().upper(),"EmployeeName":ename.strip().title(),"Password":epwd.strip()}])
                        st.session_state.employee_df = pd.concat([st.session_state.employee_df,new_row],ignore_index=True)
                        if save_to_supabase("employee_master", st.session_state.employee_df):
                            st.success("Employee added.")
                            st.rerun()
        with tab3:
            if st.session_state.employee_df.empty:
                st.info("No employees.")
            else:
                emp_del = st.selectbox("Select employee to delete", safe_col(st.session_state.employee_df,"EmployeeCode").unique())
                if st.button("Delete employee", type="primary"):
                    st.session_state.employee_df = st.session_state.employee_df[safe_col(st.session_state.employee_df,"EmployeeCode") != emp_del]
                    if save_to_supabase("employee_master", st.session_state.employee_df):
                        st.success(f"{emp_del} removed.")
                        st.rerun()

    # ── STORES ────────────────────────────────────────────────────
    elif page == "Stores":
        st.markdown("<div class='sec-head'>🏪 Stores</div>", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["  View  ","  Add  ","  Delete  "])
        with tab1:
            st.dataframe(st.session_state.gst_df, use_container_width=True, hide_index=True) if not st.session_state.gst_df.empty else st.info("No stores.")
        with tab2:
            with st.form("add_store"):
                c1,c2 = st.columns(2)
                with c1:
                    sname = st.text_input("Store Name *", placeholder="e.g. Reliance Fresh")
                    gstno = st.text_input("GST Number *", max_chars=15, placeholder="22AAAAA0000A1Z5")
                with c2:
                    city    = st.text_input("City *", placeholder="e.g. Lucknow")
                    emp_opts= safe_col(st.session_state.employee_df,"EmployeeCode").unique().tolist() or ["—"]
                    emp_sel = st.selectbox("Assign to employee *", emp_opts)
                if st.form_submit_button("Add store", type="primary"):
                    gc = gstno.strip().upper()
                    if not sname or not gc or not city: st.error("All fields required.")
                    elif not is_valid_gstin(gc): st.error("Invalid GST number.")
                    elif safe_col(st.session_state.gst_df,"GSTNumber").astype(str).str.upper().eq(gc).any(): st.error("GST already exists.")
                    else:
                        nid = f"S{len(st.session_state.gst_df)+1:05d}"
                        new_store = pd.DataFrame([{"StoreID":nid,"StoreName":sname.strip().title(),"GSTNumber":gc,"City":city.strip().title(),"EmployeeCode":emp_sel}])
                        st.session_state.gst_df = pd.concat([st.session_state.gst_df,new_store],ignore_index=True)
                        if save_to_supabase("gst_master", st.session_state.gst_df):
                            st.success("Store added.")
                            st.rerun()
        with tab3:
            if st.session_state.gst_df.empty: st.info("No stores.")
            else:
                sdel = st.selectbox("Select store to delete", safe_col(st.session_state.gst_df,"StoreID").unique())
                if st.button("Delete store", type="primary"):
                    st.session_state.gst_df = st.session_state.gst_df[safe_col(st.session_state.gst_df,"StoreID") != sdel]
                    if save_to_supabase("gst_master", st.session_state.gst_df):
                        st.success(f"{sdel} removed.")
                        st.rerun()

    # ── VIEW PLANS ────────────────────────────────────────────────
    elif page == "View Plans":
        st.markdown("<div class='sec-head'>📋 All Visit Plans</div>", unsafe_allow_html=True)
        c1,c2,c3 = st.columns(3)
        with c1: femp  = st.selectbox("Employee", ["All"]+list(safe_col(st.session_state.planned_df,"EmployeeName").dropna().unique()))
        with c2: fcity = st.selectbox("City",     ["All"]+list(safe_col(st.session_state.planned_df,"City").dropna().unique()))
        with c3: drange= st.date_input("Date range", value=(date.today()-timedelta(days=30), date.today()))
        fp = st.session_state.planned_df.copy()
        if femp !="All" and "EmployeeName" in fp.columns: fp = fp[fp["EmployeeName"]==femp]
        if fcity!="All" and "City"         in fp.columns: fp = fp[fp["City"]==fcity]
        if isinstance(drange,(list,tuple)) and len(drange)==2 and "VisitDate" in fp.columns:
            fp = fp[(fp["VisitDate"]>=drange[0])&(fp["VisitDate"]<=drange[1])]
        st.markdown(f"<div class='sec-head'>Results <span class='sec-cnt'>{len(fp)}</span></div>", unsafe_allow_html=True)
        st.dataframe(fp.sort_values("VisitDate",ascending=False) if "VisitDate" in fp.columns else fp, use_container_width=True, hide_index=True)
        download_button(fp,"admin_dl","Beat_Plan_Admin")

    # ── REFRESH ───────────────────────────────────────────────────
    elif page == "Refresh":
        st.markdown("<div class='sec-head'>🔄 Refresh Data</div>", unsafe_allow_html=True)
        st.info("Pull latest data from all Supabase tables.")
        if st.button("Refresh now", type="primary", use_container_width=True):
            st.session_state.employee_df = load_from_supabase("employee_master", EMP_COLS)
            st.session_state.gst_df      = load_from_supabase("gst_master",      GST_COLS)
            st.session_state.planned_df  = load_from_supabase("planned_visits",  PLAN_COLS)
            st.session_state.admin_df    = load_from_supabase("admin_master",    ADMIN_COLS)
            st.success("All data refreshed.")
            st.rerun()

# ====================== EMPLOYEE PAGES ======================
else:
    employee_stores = st.session_state.gst_df[
        safe_col(st.session_state.gst_df,"EmployeeCode").astype(str) == str(emp_code)
    ] if not st.session_state.gst_df.empty else pd.DataFrame(columns=GST_COLS)

    # ── DASHBOARD ─────────────────────────────────────────────────
    if page == "Dashboard":
        my = st.session_state.planned_df[safe_col(st.session_state.planned_df,"EmployeeCode").astype(str)==str(emp_code)]
        today_mine = my[my["VisitDate"]==date.today()] if "VisitDate" in my.columns else pd.DataFrame()
        tm = my[pd.to_datetime(safe_col(my,"VisitDate"),errors="coerce").dt.month==date.today().month] if "VisitDate" in my.columns else pd.DataFrame()

        render_stat_cards([
            ("#4f46e5","#eef2ff","#4f46e5","🏪", len(employee_stores),              "My stores",      f"In {safe_col(employee_stores,'City').nunique()} cities", "#9ca3af"),
            ("#06b6d4","#ecfeff","#0891b2","📋", len(my),                            "Total plans",    "↑ All time",     "#10b981"),
            ("#f59e0b","#fffbeb","#d97706","📅", len(tm),                            "This month",     "Current month",  "#9ca3af"),
            ("#10b981","#d1fae5","#059669","📍", len(today_mine),                    "Today's visits", f"Max 10 per day", "#9ca3af"),
        ])

        # Two-column layout: Available stores + Upcoming visits
        st.markdown("<div class='content-row'>", unsafe_allow_html=True)
        col_left, col_right = st.columns(2)

        with col_left:
            daily_plans = st.session_state.planned_df[
                (safe_col(st.session_state.planned_df,"EmployeeCode").astype(str)==str(emp_code)) &
                (st.session_state.planned_df["VisitDate"]==date.today())
            ] if "VisitDate" in st.session_state.planned_df.columns else pd.DataFrame(columns=PLAN_COLS)
            pc    = len(daily_plans)
            color = get_prog_color(pc)
            pct   = min(pc*10, 100)

            st.markdown(f"""
            <div class="panel-card">
                <div class="panel-header">
                    <span class="panel-icon">🏪</span>
                    Available stores
                    <span class="panel-badge">{pc} of 10</span>
                </div>
                <div class="prog-row">
                    <span class="prog-label">Daily progress</span>
                    <span class="prog-count" style="color:{color};">{pc} / 10</span>
                </div>
                <div class="prog-bg">
                    <div class="prog-fill" style="width:{pct}%;background:{color};"></div>
                </div>
            </div>""", unsafe_allow_html=True)

            # Store list
            show_cities = safe_col(employee_stores,"City").unique().tolist()
            planned_ids = safe_col(daily_plans,"StoreID").tolist()
            available   = employee_stores[~safe_col(employee_stores,"StoreID").isin(planned_ids)]

            for idx, row in available.head(5).iterrows():
                col_s, col_b = st.columns([5,1])
                with col_s:
                    st.markdown(f"""
                    <div class="store-item">
                        <div class="store-icon-wrap si-blue">🏪</div>
                        <div style="flex:1;min-width:0;">
                            <div class="store-name-txt">{row.get('StoreName','—')}</div>
                            <div class="store-meta-txt">{row.get('City','—')} · Lucknow</div>
                        </div>
                        <span class="badge badge-green">Available</span>
                    </div>""", unsafe_allow_html=True)
                with col_b:
                    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
                    if pc < 10 and st.button("+", key=f"dash_add_{idx}"):
                        new_plan = pd.DataFrame([{
                            "EmployeeCode": emp_code, "EmployeeName": emp_name,
                            "City":         row.get("City",""), "Store": row.get("StoreName",""),
                            "StoreID":      row.get("StoreID",""), "GSTNumber": row.get("GSTNumber",""),
                            "VisitDate":    date.today(),
                        }])
                        st.session_state.planned_df = pd.concat([st.session_state.planned_df, new_plan], ignore_index=True)
                        if save_to_supabase("planned_visits", st.session_state.planned_df):
                            st.success(f"Added {row.get('StoreName','')}")
                            st.rerun()

        with col_right:
            st.markdown("""
            <div class="panel-card">
                <div class="panel-header">
                    <span class="panel-icon">📅</span>
                    Upcoming visits
                </div>
            </div>""", unsafe_allow_html=True)

            if "VisitDate" in st.session_state.planned_df.columns:
                upcoming = st.session_state.planned_df[
                    (safe_col(st.session_state.planned_df,"EmployeeCode").astype(str)==str(emp_code)) &
                    (st.session_state.planned_df["VisitDate"] >= date.today())
                ].sort_values("VisitDate")

                if upcoming.empty:
                    st.info("No upcoming visits scheduled.")
                else:
                    for vdate in sorted(upcoming["VisitDate"].unique())[:4]:
                        plans     = upcoming[upcoming["VisitDate"]==vdate]
                        is_today  = vdate == date.today()
                        badge_cls = "today" if is_today else "future"
                        cities    = ", ".join(sorted(safe_col(plans,"City").dropna().unique().tolist()))
                        stores    = safe_col(plans,"Store").dropna().unique().tolist()
                        pills     = "".join(f"<span class='t-pill'>{s}</span>" for s in stores[:3])
                        if len(stores)>3: pills += f"<span class='t-pill'>+{len(stores)-3}</span>"

                        st.markdown(f"""
                        <div class="timeline-item">
                            <div class="t-date-badge {badge_cls}">
                                <div class="t-day">{vdate.strftime('%d')}</div>
                                <div class="t-mon">{vdate.strftime('%b')}</div>
                            </div>
                            <div>
                                <div class="t-stores-lbl">{len(plans)} stores planned</div>
                                <div class="t-city-lbl">{cities}</div>
                                <div class="t-pills">{pills}</div>
                            </div>
                        </div>""", unsafe_allow_html=True)
            else:
                st.info("No upcoming visits.")

        st.markdown("</div>", unsafe_allow_html=True)

    # ── BEAT PLAN ─────────────────────────────────────────────────
    elif page == "Beat Plan":
        st.markdown("<div class='sec-head'>🎯 New Beat Plan</div>", unsafe_allow_html=True)

        if employee_stores.empty:
            st.warning("No stores assigned to you yet. Contact your admin.")
            st.stop()

        c1,c2,c3 = st.columns([1,2,1])
        with c1: visit_date = st.date_input("Visit date", value=date.today(), key="beat_date")
        with c2:
            city_opts  = sorted(safe_col(employee_stores,"City").dropna().unique().tolist())
            sel_cities = st.multiselect("Filter cities (max 3)", city_opts, max_selections=3, key="city_ms")
        with c3:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            if st.button("Load stores", use_container_width=True):
                st.session_state.selected_cities = sel_cities

        daily_plans = st.session_state.planned_df[
            (safe_col(st.session_state.planned_df,"EmployeeCode").astype(str)==str(emp_code)) &
            (st.session_state.planned_df["VisitDate"]==visit_date)
        ] if "VisitDate" in st.session_state.planned_df.columns else pd.DataFrame(columns=PLAN_COLS)

        pc    = len(daily_plans)
        color = get_prog_color(pc)
        pct   = min(pc*10, 100)
        note  = "Daily limit of 10 stores reached." if pc>=10 else f"{10-pc} more store(s) can be added today."

        st.markdown(f"""
        <div class="panel-card">
            <div class="panel-header">
                <span>Daily progress</span>
                <span class="panel-badge" style="background:{'#fef2f2' if pc>=10 else '#eef2ff'};color:{'#b91c1c' if pc>=10 else '#4338ca'};">{pc} / 10</span>
            </div>
            <div class="prog-row">
                <span class="prog-label">{note}</span>
                <span class="prog-count" style="color:{color};font-weight:700;">{pc}/10</span>
            </div>
            <div class="prog-bg">
                <div class="prog-fill" style="width:{pct}%;background:{color};"></div>
            </div>
        </div>""", unsafe_allow_html=True)

        if not daily_plans.empty:
            with st.expander(f"Already planned · {pc} store(s) for {visit_date}"):
                show = [c for c in ["Store","City","GSTNumber"] if c in daily_plans.columns]
                st.dataframe(daily_plans[show], use_container_width=True, hide_index=True)

        if pc < 10:
            show_cities = st.session_state.selected_cities or safe_col(employee_stores,"City").unique().tolist()
            city_stores = employee_stores[safe_col(employee_stores,"City").isin(show_cities)]
            planned_ids = safe_col(daily_plans,"StoreID").tolist()
            available   = city_stores[~safe_col(city_stores,"StoreID").isin(planned_ids)]

            st.markdown(f"<div class='sec-head'>Available stores <span class='sec-cnt'>{len(available)}</span></div>", unsafe_allow_html=True)

            if available.empty:
                st.info("No more stores available for selected cities.")
            else:
                for idx, row in available.iterrows():
                    col1, col2 = st.columns([6,1])
                    with col1:
                        st.markdown(f"""
                        <div class="store-item">
                            <div class="store-icon-wrap si-blue">🏪</div>
                            <div style="flex:1;min-width:0;">
                                <div class="store-name-txt">{row.get('StoreName','—')}</div>
                                <div class="store-meta-txt">{row.get('City','—')} &nbsp;·&nbsp; GST: {row.get('GSTNumber','—')}</div>
                            </div>
                            <span class="badge badge-green">Available</span>
                        </div>""", unsafe_allow_html=True)
                    with col2:
                        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
                        if st.button("+ Add", key=f"add_{idx}_{visit_date}"):
                            new_plan = pd.DataFrame([{
                                "EmployeeCode": emp_code, "EmployeeName": emp_name,
                                "City":         row.get("City",""), "Store": row.get("StoreName",""),
                                "StoreID":      row.get("StoreID",""), "GSTNumber": row.get("GSTNumber",""),
                                "VisitDate":    visit_date,
                            }])
                            st.session_state.planned_df = pd.concat([st.session_state.planned_df, new_plan], ignore_index=True)
                            if save_to_supabase("planned_visits", st.session_state.planned_df):
                                st.success(f"{row.get('StoreName','')} added.")
                                st.rerun()

        st.markdown("---")
        emp_plans = st.session_state.planned_df[safe_col(st.session_state.planned_df,"EmployeeCode").astype(str)==str(emp_code)]
        download_button(emp_plans, "emp_dl", f"Beat_Plan_{emp_code}")

    # ── MY PLANS ──────────────────────────────────────────────────
    elif page == "My Plans":
        st.markdown("<div class='sec-head'>📅 My Plans</div>", unsafe_allow_html=True)
        my = st.session_state.planned_df[safe_col(st.session_state.planned_df,"EmployeeCode").astype(str)==str(emp_code)]
        if my.empty:
            st.info("You haven't created any plans yet.")
        else:
            render_stat_cards([
                ("#4f46e5","#eef2ff","#4f46e5","📋", len(my),                                     "Total plans",   "All time",      "#9ca3af"),
                ("#06b6d4","#ecfeff","#0891b2","📍", safe_col(my,"City").nunique(),               "Cities covered","—",            "#9ca3af"),
                ("#f59e0b","#fffbeb","#d97706","📅", len(safe_col(my,"VisitDate").unique()),       "Unique dates",  "—",            "#9ca3af"),
                ("#10b981","#d1fae5","#059669","🏪", safe_col(my,"Store").nunique(),               "Unique stores", "—",            "#9ca3af"),
            ])
            st.dataframe(
                my.sort_values("VisitDate",ascending=False) if "VisitDate" in my.columns else my,
                use_container_width=True, hide_index=True)
            download_button(my, "my_dl", f"My_Plans_{emp_code}")

    # ── ANALYTICS ─────────────────────────────────────────────────
    elif page == "Analytics":
        st.markdown("<div class='sec-head'>📊 Analytics</div>", unsafe_allow_html=True)
        my = st.session_state.planned_df[safe_col(st.session_state.planned_df,"EmployeeCode").astype(str)==str(emp_code)]
        if my.empty:
            st.info("No data yet.")
        else:
            tm = my[pd.to_datetime(safe_col(my,"VisitDate"),errors="coerce").dt.month==date.today().month] if "VisitDate" in my.columns else pd.DataFrame()
            render_stat_cards([
                ("#4f46e5","#eef2ff","#4f46e5","📋", len(my),                       "Total visits",   "All time",   "#9ca3af"),
                ("#06b6d4","#ecfeff","#0891b2","📍", safe_col(my,"City").nunique(), "Cities",         "—",         "#9ca3af"),
                ("#f59e0b","#fffbeb","#d97706","🏪", safe_col(my,"Store").nunique(),"Unique stores",  "—",         "#9ca3af"),
                ("#10b981","#d1fae5","#059669","📅", len(tm),                       "This month",     "Current",   "#9ca3af"),
            ])
            st.markdown("---")
            c1,c2 = st.columns(2)
            with c1:
                st.markdown("<div class='sec-head'>Visits by city</div>", unsafe_allow_html=True)
                if "City" in my.columns: st.bar_chart(my.groupby("City").size(), color="#4f46e5")
            with c2:
                st.markdown("<div class='sec-head'>Visits over time</div>", unsafe_allow_html=True)
                if "VisitDate" in my.columns:
                    tmp = my.copy()
                    tmp["Month"] = pd.to_datetime(tmp["VisitDate"],errors="coerce").dt.to_period("M").astype(str)
                    st.line_chart(tmp.groupby("Month").size(), color="#06b6d4")

    # ── UPCOMING ──────────────────────────────────────────────────
    elif page == "Upcoming":
        st.markdown("<div class='sec-head'>📆 Upcoming Visits</div>", unsafe_allow_html=True)
        if "VisitDate" not in st.session_state.planned_df.columns:
            st.info("No upcoming visits.")
        else:
            upcoming = st.session_state.planned_df[
                (safe_col(st.session_state.planned_df,"EmployeeCode").astype(str)==str(emp_code)) &
                (st.session_state.planned_df["VisitDate"] >= date.today())
            ].sort_values("VisitDate")
            if upcoming.empty:
                st.info("No upcoming visits scheduled.")
            else:
                for vdate in sorted(upcoming["VisitDate"].unique()):
                    plans     = upcoming[upcoming["VisitDate"]==vdate]
                    is_today  = vdate == date.today()
                    badge_cls = "today" if is_today else "future"
                    cities    = ", ".join(sorted(safe_col(plans,"City").dropna().unique().tolist()))
                    stores    = safe_col(plans,"Store").dropna().unique().tolist()
                    pills     = "".join(f"<span class='t-pill'>{s}</span>" for s in stores[:4])
                    if len(stores)>4: pills += f"<span class='t-pill'>+{len(stores)-4}</span>"
                    st.markdown(f"""
                    <div class="timeline-item">
                        <div class="t-date-badge {badge_cls}">
                            <div class="t-day">{vdate.strftime('%d')}</div>
                            <div class="t-mon">{vdate.strftime('%b')}</div>
                        </div>
                        <div>
                            <div class="t-stores-lbl">{len(plans)} stores planned</div>
                            <div class="t-city-lbl">{cities}</div>
                            <div class="t-pills">{pills}</div>
                        </div>
                    </div>""", unsafe_allow_html=True)

    # ── ADD STORE ─────────────────────────────────────────────────
    elif page == "Add Store":
        st.markdown("<div class='sec-head'>➕ Add New Store</div>", unsafe_allow_html=True)
        with st.form("store_req"):
            c1,c2 = st.columns(2)
            with c1:
                sname = st.text_input("Store Name *", placeholder="e.g. Big Bazaar")
                city  = st.text_input("City *",       placeholder="e.g. Lucknow")
            with c2:
                gst = st.text_input("GST Number *", max_chars=15, placeholder="22AAAAA0000A1Z5")
                st.text_area("Remarks (optional)", height=100, placeholder="Any notes...")
            if st.form_submit_button("Add store", type="primary"):
                gc = gst.strip().upper()
                if not sname or not city or not gc: st.error("All fields are required.")
                elif not is_valid_gstin(gc): st.error("Invalid GST number.")
                elif safe_col(st.session_state.gst_df,"GSTNumber").astype(str).str.upper().eq(gc).any(): st.error("GST already exists.")
                else:
                    nid = f"S{len(st.session_state.gst_df)+1:05d}"
                    new_store = pd.DataFrame([{"StoreID":nid,"StoreName":sname.strip().title(),"GSTNumber":gc,"City":city.strip().title(),"EmployeeCode":emp_code}])
                    st.session_state.gst_df = pd.concat([st.session_state.gst_df,new_store],ignore_index=True)
                    if save_to_supabase("gst_master", st.session_state.gst_df):
                        st.success(f"'{sname.title()}' added.")
                        st.rerun()

# ====================== FOOTER ======================
st.markdown("---")
st.caption("Beat Plan Pro · 2026 · Built by Bipin Pandey")
