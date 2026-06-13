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

# ====================== SUPABASE ======================
SUPABASE_URL = "https://kueicdruccvbempjvxzn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt1ZWljZHJ1Y2N2YmVtcGp2eHpuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODExMjE0MTcsImV4cCI6MjA5NjY5NzQxN30.aWkQ85Wq-iP2Gp1W1dfoATdRhR0rFcc1H6CGtK_zDE0"
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"❌ Supabase connection failed: {e}"); st.stop()

# ====================== CSS ======================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { background: #f4f6fb !important; }
.block-container { padding: 1.25rem 2rem 5rem 2rem !important; max-width: 1160px !important; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="collapsedControl"] { display: none !important; }

/* ── TOP NAV ── */
.topnav {
    background: #fff; border: 1px solid #e2e5ef;
    border-radius: 18px; padding: 11px 22px;
    display: flex; align-items: center; gap: 6px;
    margin-bottom: 1.4rem;
    box-shadow: 0 2px 14px rgba(0,0,0,0.05);
}
.tn-logo {
    display: flex; align-items: center; gap: 9px;
    font-size: 15px; font-weight: 800; color: #18181b;
    margin-right: 12px; white-space: nowrap; letter-spacing: -0.3px;
    text-decoration: none;
}
.tn-icon {
    width: 32px; height: 32px; border-radius: 9px;
    background: linear-gradient(135deg,#4f46e5,#7c3aed);
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(79,70,229,.28);
}
.tn-links { display: flex; gap: 2px; flex: 1; }
.tn-btn {
    padding: 7px 15px; border-radius: 10px;
    font-size: 13px; font-weight: 500;
    border: 1px solid transparent; background: transparent;
    color: #6b7280; cursor: pointer; transition: all .15s;
    white-space: nowrap; display: flex; align-items: center; gap: 5px;
}
.tn-btn:hover { background: #f4f6fb; color: #374151; }
.tn-btn.active {
    background: #4f46e5; color: #fff;
    border-color: #4f46e5;
    box-shadow: 0 2px 8px rgba(79,70,229,.28);
}
.tn-right { display: flex; align-items: center; gap: 9px; margin-left: auto; }
.tn-avatar {
    width: 34px; height: 34px; border-radius: 50%;
    background: linear-gradient(135deg,#4f46e5,#06b6d4);
    color: #fff; font-size: 12px; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 2px 8px rgba(79,70,229,.25); flex-shrink: 0;
}
.tn-uname { font-size: 13px; font-weight: 600; color: #374151; }
.tn-role {
    font-size: 10.5px; padding: 2px 9px; border-radius: 20px;
    font-weight: 600; background: #eef2ff; color: #4338ca;
}

/* ── PAGE HEADER ── */
.page-hdr { margin-bottom: 1.25rem; }
.page-title { font-size: 21px; font-weight: 800; color: #18181b; letter-spacing: -0.5px; }
.page-sub   { font-size: 13px; color: #9ca3af; margin-top: 3px; }

/* ── STAT CARDS ── */
.stats-grid {
    display: grid; grid-template-columns: repeat(4,minmax(0,1fr));
    gap: 12px; margin-bottom: 1.4rem;
}
.stat-card {
    background: #fff; border: 1px solid #e2e5ef;
    border-radius: 16px; padding: 18px 20px;
    position: relative; overflow: hidden;
    box-shadow: 0 2px 10px rgba(0,0,0,.04);
    transition: transform .15s, box-shadow .15s;
}
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,.08); }
.stat-top-bar { position: absolute; top:0; left:0; width:100%; height:3px; }
.stat-icon {
    width: 40px; height: 40px; border-radius: 11px;
    display: flex; align-items: center; justify-content: center;
    font-size: 19px; margin-bottom: 13px;
}
.stat-val  { font-size: 28px; font-weight: 800; color: #18181b; letter-spacing: -1px; line-height: 1; }
.stat-lbl  { font-size: 12px; color: #9ca3af; margin-top: 4px; font-weight: 500; }
.stat-foot {
    font-size: 11.5px; font-weight: 600; margin-top: 10px;
    padding-top: 9px; border-top: 1px solid #f4f6fb;
}

/* ── CARDS / PANELS ── */
.card {
    background: #fff; border: 1px solid #e2e5ef;
    border-radius: 16px; padding: 20px 22px;
    box-shadow: 0 2px 10px rgba(0,0,0,.04);
    margin-bottom: 14px;
}
.card-hdr {
    display: flex; align-items: center; gap: 9px;
    font-size: 14px; font-weight: 700; color: #18181b;
    padding-bottom: 12px; margin-bottom: 14px;
    border-bottom: 1px solid #f4f6fb;
}
.card-hdr-icon {
    width: 30px; height: 30px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center; font-size: 15px;
}
.card-pill {
    font-size: 11px; padding: 3px 10px; border-radius: 20px; font-weight: 600; margin-left: auto;
}

/* ── PROGRESS ── */
.prog-wrap { margin-bottom: 4px; }
.prog-row  { display: flex; justify-content: space-between; align-items: center; margin-bottom: 7px; }
.prog-lbl  { font-size: 13px; font-weight: 600; color: #374151; }
.prog-num  { font-size: 13px; font-weight: 700; }
.prog-track { height: 8px; background: #f4f6fb; border-radius: 99px; overflow: hidden; }
.prog-fill  { height: 100%; border-radius: 99px; transition: width .4s ease; }
.prog-hint  { font-size: 12px; color: #9ca3af; margin-top: 7px; }

/* ── STORE ROWS ── */
.store-row {
    display: flex; align-items: center; gap: 12px;
    padding: 11px 14px; border-radius: 12px;
    margin-bottom: 6px; background: #f9fafb;
    border: 1px solid #f0f2f8; transition: all .15s;
}
.store-row:hover { background: #f4f6fb; border-color: #e2e5ef; }
.store-av {
    width: 38px; height: 38px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 17px; flex-shrink: 0;
}
.av-i { background: #eef2ff; }
.av-r { background: #fef2f2; }
.av-g { background: #f0fdf4; }
.av-a { background: #fffbeb; }
.s-nm { font-size: 13.5px; font-weight: 600; color: #18181b; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.s-mt { font-size: 12px; color: #9ca3af; margin-top: 2px; }

/* ── BADGES ── */
.bdg { font-size: 11px; padding: 4px 10px; border-radius: 20px; font-weight: 600; white-space: nowrap; flex-shrink: 0; }
.bdg-g  { background: #dcfce7; color: #15803d; }
.bdg-r  { background: #fee2e2; color: #b91c1c; }
.bdg-a  { background: #fef9c3; color: #854d0e; }
.bdg-p  { background: #ede9fe; color: #6d28d9; }
.bdg-b  { background: #dbeafe; color: #1d4ed8; }
.bdg-gr { background: #f3f4f6; color: #6b7280; }

/* ── TIMELINE ── */
.tl-item {
    display: flex; gap: 13px; align-items: flex-start;
    padding: 12px 14px; border-radius: 12px; background: #f9fafb;
    border: 1px solid #f0f2f8; margin-bottom: 8px;
    transition: all .15s;
}
.tl-item:hover { background: #f4f6fb; border-color: #e2e5ef; }
.tl-date {
    width: 46px; flex-shrink: 0; text-align: center;
    border-radius: 11px; padding: 8px 4px;
}
.tl-date.tod { background: linear-gradient(135deg,#4f46e5,#7c3aed); box-shadow: 0 3px 10px rgba(79,70,229,.28); }
.tl-date.fut { background: #fff; border: 1px solid #e2e5ef; }
.tl-day { font-size: 20px; font-weight: 800; line-height: 1; }
.tl-mon { font-size: 9.5px; text-transform: uppercase; letter-spacing: .06em; margin-top: 2px; }
.tl-date.tod .tl-day,.tl-date.tod .tl-mon { color: #fff; }
.tl-date.fut .tl-day { color: #18181b; }
.tl-date.fut .tl-mon { color: #9ca3af; }
.tl-title { font-size: 13.5px; font-weight: 700; color: #18181b; margin-bottom: 2px; }
.tl-sub   { font-size: 12px; color: #9ca3af; margin-bottom: 6px; }
.tl-pills { display: flex; flex-wrap: wrap; gap: 4px; }
.tl-pill  { font-size: 11px; background: #fff; border: 1px solid #e2e5ef; color: #4b5563; padding: 2px 8px; border-radius: 20px; }

/* ── QUICK ACTIONS ── */
.qa-row { display: grid; grid-template-columns: repeat(3,minmax(0,1fr)); gap: 10px; margin-bottom: 1.2rem; }
.qa-card {
    background: #fff; border: 1px solid #e2e5ef;
    border-radius: 14px; padding: 16px 18px;
    display: flex; align-items: center; gap: 13px;
    box-shadow: 0 2px 8px rgba(0,0,0,.03);
    transition: all .15s; cursor: pointer;
}
.qa-card:hover { transform: translateY(-2px); box-shadow: 0 6px 18px rgba(0,0,0,.08); border-color: #c7d2fe; }
.qa-icon { width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; }
.qa-title { font-size: 13.5px; font-weight: 700; color: #18181b; }
.qa-desc  { font-size: 12px; color: #9ca3af; margin-top: 2px; }

/* ── SECTION HEADING ── */
.sec-hd {
    font-size: 15px; font-weight: 700; color: #18181b;
    margin: 1.3rem 0 10px; display: flex; align-items: center; gap: 8px;
}
.sec-ct { font-size: 11px; background: #f4f6fb; color: #6b7280; padding: 2px 9px; border-radius: 20px; font-weight: 600; }

/* ── EMPTY STATE ── */
.empty { text-align: center; padding: 3rem 1rem; }
.empty-icon { font-size: 40px; margin-bottom: 10px; }
.empty-title { font-size: 14.5px; font-weight: 700; color: #374151; }
.empty-sub   { font-size: 13px; color: #9ca3af; margin-top: 4px; }

/* ── INFO BOX ── */
.info-box {
    background: #eef2ff; border: 1px solid #c7d2fe;
    border-radius: 12px; padding: 14px 18px;
    font-size: 13.5px; color: #3730a3; margin-bottom: 16px;
    display: flex; gap: 10px; align-items: flex-start;
}

/* ── WARNING BOX ── */
.warn-box {
    background: #fffbeb; border: 1px solid #fcd34d;
    border-radius: 12px; padding: 14px 18px;
    font-size: 13.5px; color: #92400e; margin-bottom: 16px;
    display: flex; gap: 10px; align-items: flex-start;
}

/* ── LOGIN ── */
.lg-wrap { max-width: 420px; margin: 2rem auto 0; }
.lg-top  { text-align: center; margin-bottom: 2rem; }
.lg-icon {
    width: 60px; height: 60px; border-radius: 18px;
    background: linear-gradient(135deg,#4f46e5,#7c3aed);
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 28px; color: #fff; margin-bottom: 14px;
    box-shadow: 0 6px 20px rgba(79,70,229,.3);
}
.lg-title { font-size: 24px; font-weight: 800; color: #18181b; letter-spacing: -0.5px; }
.lg-sub   { font-size: 13.5px; color: #9ca3af; margin-top: 5px; }
.lg-card  {
    background: #fff; border: 1px solid #e2e5ef;
    border-radius: 20px; padding: 28px 30px;
    box-shadow: 0 8px 32px rgba(0,0,0,.07);
}
.lg-lbl { font-size: 12.5px; font-weight: 600; color: #374151; margin-bottom: 5px; }

/* ── STREAMLIT OVERRIDES ── */
.stButton > button {
    border-radius: 10px !important; height: 42px !important;
    font-weight: 600 !important; font-size: 13.5px !important;
    background: #4f46e5 !important; color: #fff !important;
    border: none !important; letter-spacing: .1px !important;
    box-shadow: 0 2px 8px rgba(79,70,229,.2) !important;
    transition: all .15s !important;
}
.stButton > button:hover {
    background: #4338ca !important;
    box-shadow: 0 4px 14px rgba(79,70,229,.35) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

.stTextInput > div > div > input {
    border-radius: 10px !important; border: 1.5px solid #e2e5ef !important;
    font-size: 13.5px !important; background: #fafbff !important;
    padding: 10px 13px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #4f46e5 !important; background: #fff !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,.1) !important;
}
.stTextInput > div > div > input::placeholder { color: #c4c9d9 !important; }

.stSelectbox > div > div,
.stMultiSelect > div > div {
    border-radius: 10px !important; border: 1.5px solid #e2e5ef !important;
    background: #fafbff !important;
}
.stDateInput > div > div > input {
    border-radius: 10px !important; border: 1.5px solid #e2e5ef !important;
}
.stTextArea > div > div > textarea {
    border-radius: 10px !important; border: 1.5px solid #e2e5ef !important;
    font-size: 13.5px !important; background: #fafbff !important;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 3px; background: #f0f2f8; border-radius: 12px; padding: 4px; border: none !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px !important; font-size: 13px !important; font-weight: 500 !important;
    padding: 7px 20px !important; color: #6b7280 !important;
    background: transparent !important; border: none !important;
}
.stTabs [aria-selected="true"] {
    background: #fff !important; color: #18181b !important;
    font-weight: 700 !important; box-shadow: 0 1px 6px rgba(0,0,0,.08) !important;
}
.stDataFrame { border-radius: 14px !important; border: 1px solid #e2e5ef !important; overflow: hidden !important; }
.stAlert { border-radius: 12px !important; font-size: 13.5px !important; }
.stDownloadButton > button {
    background: #f9fafb !important; color: #374151 !important;
    border: 1.5px solid #e2e5ef !important; border-radius: 10px !important;
    font-weight: 600 !important; box-shadow: none !important;
}
.stDownloadButton > button:hover { background: #f0f2f8 !important; transform: none !important; }
.streamlit-expanderHeader {
    background: #f9fafb !important; border-radius: 12px !important;
    font-size: 13.5px !important; font-weight: 600 !important;
    border: 1px solid #e2e5ef !important; color: #374151 !important;
}
hr { border-color: #e2e5ef !important; margin: 1.5rem 0 !important; }

[data-testid="stSidebar"] {
    background: #fff !important; border-right: 1px solid #e2e5ef !important;
}
[data-testid="stSidebar"] .stRadio > label { display: none; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] { gap: 1px !important; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    background: transparent !important; border: none !important;
    border-left: 3px solid transparent !important;
    border-radius: 0 10px 10px 0 !important;
    padding: 10px 16px !important; font-size: 13.5px !important;
    font-weight: 500 !important; color: #6b7280 !important;
    cursor: pointer !important; width: 100% !important; transition: all .15s !important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) {
    background: #eef2ff !important; color: #4f46e5 !important;
    border-left-color: #4f46e5 !important; font-weight: 700 !important;
}
[data-testid="stMetric"] {
    background: #fff !important; border: 1px solid #e2e5ef !important;
    border-radius: 14px !important; padding: 16px 18px !important;
}
.stRadio [data-testid="stMarkdownContainer"] p { margin: 0 !important; }
</style>
""", unsafe_allow_html=True)

# ====================== DB HELPERS ======================
COLUMN_MAP = {
    "EmployeeCode": ["employeecode","employee_code"],
    "EmployeeName": ["employeename","employee_name"],
    "Password":     ["password"],
    "StoreID":      ["storeid","store_id"],
    "StoreName":    ["storename","store_name"],
    "GSTNumber":    ["gstnumber","gst_number"],
    "City":         ["city"], "Store": ["store"],
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
            if key in lower_map: rename[lower_map[key]] = expected; break
    return df.rename(columns=rename) if rename else df

def init_db():
    try: supabase.table("planned_visits").select("*").limit(1).execute(); return True
    except Exception as e: st.error(f"Supabase error: {e}"); return False

def clean_dataframe(df, cols):
    if df.empty: return df
    df = normalize_columns(df)
    for col in cols:
        if col not in df.columns: df[col] = ""
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()
    if "VisitDate" in df.columns:
        df["VisitDate"] = pd.to_datetime(df["VisitDate"], errors="coerce").dt.date
    return df

def load_from_supabase(table, columns):
    try:
        all_rows, bs, off = [], 1000, 0
        while True:
            r = supabase.table(table).select("*").range(off, off+bs-1).execute()
            if not r.data: break
            all_rows.extend(r.data)
            if len(r.data) < bs: break
            off += bs
        return clean_dataframe(pd.DataFrame(all_rows), columns) if all_rows else pd.DataFrame(columns=columns)
    except Exception as e:
        st.warning(f"Could not load `{table}`: {e}")
        return pd.DataFrame(columns=columns)

def sanitize_for_json(df):
    import math
    d = df.copy()
    for col in d.columns:
        if pd.api.types.is_float_dtype(d[col]):
            d[col] = d[col].apply(lambda x: None if (x is None or (isinstance(x,float) and (math.isnan(x) or math.isinf(x)))) else x)
        elif d[col].dtype == object:
            d[col] = d[col].apply(lambda x: None if (x is None or (isinstance(x,str) and x.lower() in ("nan","none",""))) else x)
    return d.where(pd.notnull(d), None)

def save_to_supabase(table, df):
    try:
        d = df.copy()
        if "id" in d.columns: d = d.drop("id", axis=1)
        for col in d.columns:
            if col == "VisitDate" or pd.api.types.is_datetime64_any_dtype(d[col]):
                d[col] = pd.to_datetime(d[col], errors="coerce").dt.strftime("%Y-%m-%d")
        d = sanitize_for_json(d)
        try: supabase.table(table).delete().neq("id",-1).execute()
        except: pass
        if not d.empty:
            recs = [{k:v for k,v in r.items() if v is not None} for r in d.to_dict("records")]
            for i in range(0, len(recs), 100):
                supabase.table(table).insert(recs[i:i+100]).execute()
        return True
    except Exception as e:
        st.error(f"Save failed: {e}"); return False

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

defaults = {"logged_in":False,"role":"","emp_code":"","emp_name":"","page":"Dashboard","selected_cities":[]}
for k,v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

# ====================== UTIL FNS ======================
def is_valid_gstin(g):
    return bool(re.match(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$", str(g).strip().upper()))

def safe_col(df, col):
    return df[col] if col in df.columns else pd.Series([""]*len(df))

def get_initials(name):
    p = str(name).strip().split()
    return (p[0][0]+p[-1][0]).upper() if len(p)>=2 else name[:2].upper()

def prog_color(pc):
    return "#4f46e5" if pc<8 else "#f59e0b" if pc<10 else "#ef4444"

def go(page):
    st.session_state.page = page; st.rerun()

def download_btn(df, key, prefix="Beat_Plan"):
    if not df.empty:
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine="openpyxl") as w:
            df.to_excel(w, index=False, sheet_name="Beat Plan")
        out.seek(0)
        st.download_button("⬇  Export to Excel", data=out.getvalue(),
            file_name=f"{prefix}_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True, key=key)

def render_nav(name, role, page, nav_pages):
    icons = {
        "Dashboard":"📊","Employees":"👥","Stores":"🏪","View Plans":"📋","Refresh":"🔄",
        "Beat Plan":"🎯","My Plans":"📅","Upcoming":"📆","Analytics":"📈","Add Store":"➕"
    }
    ini      = get_initials(name) if name else "??"
    role_lbl = "Admin" if role=="admin" else "Field Rep"

    # Brand + user chip (HTML only — purely decorative)
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;
                background:#fff;border:1px solid #e2e5ef;border-radius:18px;
                padding:10px 22px;margin-bottom:8px;
                box-shadow:0 2px 14px rgba(0,0,0,.05);">
        <div style="display:flex;align-items:center;gap:9px;font-size:15px;
                    font-weight:800;color:#18181b;letter-spacing:-0.3px;">
            <div style="width:32px;height:32px;border-radius:9px;
                        background:linear-gradient(135deg,#4f46e5,#7c3aed);
                        display:flex;align-items:center;justify-content:center;
                        font-size:16px;box-shadow:0 2px 8px rgba(79,70,229,.28);">🗺️</div>
            Beat Plan Pro
        </div>
        <div style="display:flex;align-items:center;gap:9px;">
            <div style="width:34px;height:34px;border-radius:50%;
                        background:linear-gradient(135deg,#4f46e5,#06b6d4);
                        color:#fff;font-size:12px;font-weight:700;
                        display:flex;align-items:center;justify-content:center;
                        box-shadow:0 2px 8px rgba(79,70,229,.25);">{ini}</div>
            <div style="font-size:13px;font-weight:600;color:#374151;">{name}</div>
            <span style="font-size:10.5px;padding:2px 9px;border-radius:20px;
                         font-weight:600;background:#eef2ff;color:#4338ca;">{role_lbl}</span>
        </div>
    </div>""", unsafe_allow_html=True)

    # Real nav buttons in a styled row
    st.markdown("""
    <style>
    /* Nav button row wrapper */
    div[data-testid="stHorizontalBlock"].nav-row > div {
        flex: 0 0 auto !important;
    }
    /* Style all nav buttons */
    .nav-row .stButton > button {
        background: transparent !important;
        color: #6b7280 !important;
        border: 1px solid #e2e5ef !important;
        border-radius: 10px !important;
        height: 38px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        box-shadow: none !important;
        padding: 0 14px !important;
    }
    .nav-row .stButton > button:hover {
        background: #f4f6fb !important;
        color: #374151 !important;
        transform: none !important;
        box-shadow: none !important;
    }
    </style>""", unsafe_allow_html=True)

    nav_cols = st.columns(len(nav_pages) + 2)
    for i, p in enumerate(nav_pages):
        with nav_cols[i]:
            label = f"{icons.get(p,'')} {p}"
            # Active page button gets filled style via extra CSS class trick
            if page == p:
                st.markdown(f"""
                <style>
                div[data-testid="stHorizontalBlock"] > div:nth-child({i+1}) .stButton > button {{
                    background: #4f46e5 !important;
                    color: #fff !important;
                    border-color: #4f46e5 !important;
                    font-weight: 700 !important;
                    box-shadow: 0 2px 8px rgba(79,70,229,.28) !important;
                }}
                </style>""", unsafe_allow_html=True)
            if st.button(label, key=f"nav_{p}", use_container_width=True):
                go(p)

def stat_cards(items):
    html = "<div class='stats-grid'>"
    for bar, ibg, ico, val, lbl, foot, fc in items:
        html += f"""
        <div class="stat-card">
            <div class="stat-top-bar" style="background:{bar}"></div>
            <div class="stat-icon" style="background:{ibg};">{ico}</div>
            <div class="stat-val">{val}</div>
            <div class="stat-lbl">{lbl}</div>
            <div class="stat-foot" style="color:{fc};">{foot}</div>
        </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

def empty(icon, title, sub=""):
    st.markdown(f"""
    <div class="empty">
        <div class="empty-icon">{icon}</div>
        <div class="empty-title">{title}</div>
        <div class="empty-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

def page_hdr(title, sub=""):
    st.markdown(f"""
    <div class="page-hdr">
        <div class="page-title">{title}</div>
        {"<div class='page-sub'>"+sub+"</div>" if sub else ""}
    </div>""", unsafe_allow_html=True)

def info_box(msg):
    st.markdown(f'<div class="info-box">ℹ️ &nbsp;{msg}</div>', unsafe_allow_html=True)

def warn_box(msg):
    st.markdown(f'<div class="warn-box">⚠️ &nbsp;{msg}</div>', unsafe_allow_html=True)

# ====================== LOGIN ======================
if not st.session_state.logged_in:
    st.markdown("<div class='lg-wrap'>", unsafe_allow_html=True)
    st.markdown("""
        <div class="lg-top">
            <div class="lg-icon">🗺️</div>
            <div class="lg-title">Beat Plan Pro</div>
            <div class="lg-sub">Smart store visit planning for field teams</div>
        </div>""", unsafe_allow_html=True)

    login_type = st.radio("Role", ["🛡️  Admin","👷  Employee"], horizontal=True, label_visibility="collapsed")
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    is_admin = "Admin" in login_type

    with st.container():
        if is_admin:
            st.markdown("<div class='lg-lbl'>Username</div>", unsafe_allow_html=True)
            user = st.text_input("u", placeholder="Admin username", key="au", label_visibility="collapsed")
            st.markdown("<div class='lg-lbl'>Password</div>", unsafe_allow_html=True)
            pwd  = st.text_input("p", type="password", placeholder="Password", key="ap", label_visibility="collapsed")
            if st.button("Sign in as Admin  →", type="primary", use_container_width=True):
                if not user or not pwd:
                    st.error("Please enter both username and password.")
                else:
                    df = st.session_state.admin_df
                    ok = (
                        (df["Username"].astype(str).str.strip()==user.strip()) &
                        (df["Password"].astype(str).str.strip()==pwd.strip())
                    ) if "Username" in df.columns else pd.Series([False])
                    if ok.any():
                        st.session_state.update(logged_in=True,role="admin",emp_name="Admin",page="Dashboard"); st.rerun()
                    else:
                        st.error(f"❌ Incorrect credentials. ({len(df)} admin record(s) found)")
        else:
            st.markdown("<div class='lg-lbl'>Employee Code</div>", unsafe_allow_html=True)
            ec = st.text_input("ec", placeholder="e.g. EMP001", key="ec", label_visibility="collapsed")
            st.markdown("<div class='lg-lbl'>Password</div>", unsafe_allow_html=True)
            ep = st.text_input("ep", type="password", placeholder="Password", key="ep", label_visibility="collapsed")
            if st.button("Sign in as Employee  →", type="primary", use_container_width=True):
                if not ec or not ep:
                    st.error("Please enter your employee code and password.")
                else:
                    df = st.session_state.employee_df
                    match = df[
                        (df["EmployeeCode"].astype(str).str.strip()==ec.strip()) &
                        (df["Password"].astype(str).str.strip()==ep.strip())
                    ] if "EmployeeCode" in df.columns else pd.DataFrame()
                    if not match.empty:
                        st.session_state.update(
                            logged_in=True, role="employee",
                            emp_code=str(match.iloc[0]["EmployeeCode"]),
                            emp_name=match.iloc[0]["EmployeeName"],
                            page="Dashboard"); st.rerun()
                    else:
                        st.error(f"❌ Incorrect credentials. ({len(df)} employee record(s) found)")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ====================== MAIN ======================
role     = st.session_state.role
emp_code = st.session_state.emp_code
emp_name = st.session_state.emp_name
page     = st.session_state.page

if role == "admin":
    nav_pages = ["Dashboard","Employees","Stores","View Plans","Refresh"]
else:
    nav_pages = ["Dashboard","Beat Plan","My Plans","Upcoming","Analytics","Add Store"]

# ── Single top nav bar with real Streamlit buttons ───────
render_nav(emp_name, role, page, nav_pages)

# Sidebar: sign out
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.markdown("---")
    if st.button("🚪  Sign Out", use_container_width=True, key="signout"):
        for k,v in defaults.items(): st.session_state[k] = v
        st.rerun()
    st.markdown("---")
    st.caption(f"Signed in as **{emp_name}**\n\n{date.today().strftime('%d %b %Y')}")

page = st.session_state.page  # re-read

# ====================== ADMIN PAGES ======================
if role == "admin":
    today_plans = int((st.session_state.planned_df["VisitDate"]==date.today()).sum()) \
        if "VisitDate" in st.session_state.planned_df.columns else 0

    # ── Dashboard ─────────────────────────────────────────
    if page == "Dashboard":
        page_hdr("Admin Dashboard 📊",
                 f"{date.today().strftime('%A, %d %B %Y')}  ·  Overview of all field activity")

        stat_cards([
            ("linear-gradient(90deg,#4f46e5,#7c3aed)","#eef2ff","👥",
             len(st.session_state.employee_df),"Total Employees","↑ Active field team","#4f46e5"),
            ("linear-gradient(90deg,#06b6d4,#0284c7)","#ecfeff","🏪",
             len(st.session_state.gst_df),"Total Stores","↑ Store coverage","#0891b2"),
            ("linear-gradient(90deg,#f59e0b,#d97706)","#fffbeb","📋",
             len(st.session_state.planned_df),"All Plans","↑ Total planned visits","#d97706"),
            ("linear-gradient(90deg,#10b981,#059669)","#d1fae5","📍",
             today_plans,"Today's Visits","Scheduled for today","#059669"),
        ])

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div class='sec-hd'>📋 Recent Beat Plans</div>", unsafe_allow_html=True)
            df_show = st.session_state.planned_df
            if not df_show.empty:
                if "VisitDate" in df_show.columns:
                    df_show = df_show.sort_values("VisitDate", ascending=False)
                st.dataframe(df_show.head(8), use_container_width=True, hide_index=True)
            else:
                empty("📋","No plans yet","Plans appear here once employees start planning visits.")

        with c2:
            st.markdown("<div class='sec-hd'>👥 Employees</div>", unsafe_allow_html=True)
            disp = st.session_state.employee_df.drop(columns=["Password"], errors="ignore")
            if not disp.empty:
                st.dataframe(disp, use_container_width=True, hide_index=True)
            else:
                empty("👥","No employees","Add employees to get started.")

    # ── Employees ─────────────────────────────────────────
    elif page == "Employees":
        page_hdr("Manage Employees 👥","Add, view, or remove field team members")
        tab1, tab2, tab3 = st.tabs(["  👁  View All  ","  ➕  Add Employee  ","  🗑  Remove  "])

        with tab1:
            disp = st.session_state.employee_df.drop(columns=["Password"], errors="ignore")
            if not disp.empty:
                st.markdown(f"<p style='font-size:13px;color:#9ca3af;margin-bottom:8px;'>{len(disp)} employees in system</p>", unsafe_allow_html=True)
                st.dataframe(disp, use_container_width=True, hide_index=True)
            else:
                empty("👥","No employees yet","Use the Add Employee tab to add your first team member.")

        with tab2:
            info_box("Employee code must be unique. The employee will use this code + password to log in.")
            with st.form("add_emp", clear_on_submit=True):
                c1,c2 = st.columns(2)
                with c1:
                    ecode = st.text_input("Employee Code *", placeholder="e.g. EMP042")
                    ename = st.text_input("Full Name *",     placeholder="e.g. Ramesh Kumar")
                with c2:
                    epwd  = st.text_input("Password *", type="password", placeholder="Set a secure password")
                    st.markdown("<div style='height:27px'></div>", unsafe_allow_html=True)
                if st.form_submit_button("➕  Add Employee", type="primary", use_container_width=True):
                    if not ecode or not ename or not epwd:
                        st.error("⚠️ All three fields are required.")
                    elif safe_col(st.session_state.employee_df,"EmployeeCode").astype(str).str.upper().eq(ecode.strip().upper()).any():
                        st.error(f"⚠️ Code **{ecode.strip().upper()}** already exists. Use a different code.")
                    else:
                        nr = pd.DataFrame([{"EmployeeCode":ecode.strip().upper(),"EmployeeName":ename.strip().title(),"Password":epwd.strip()}])
                        st.session_state.employee_df = pd.concat([st.session_state.employee_df,nr],ignore_index=True)
                        if save_to_supabase("employee_master", st.session_state.employee_df):
                            st.success(f"✅ **{ename.strip().title()}** added successfully!"); st.rerun()

        with tab3:
            if st.session_state.employee_df.empty:
                empty("👥","No employees to remove","")
            else:
                warn_box("Removing an employee is permanent. Their store assignments remain but they cannot log in.")
                emp_del = st.selectbox("Choose employee to remove",
                    safe_col(st.session_state.employee_df,"EmployeeCode").unique())
                row = st.session_state.employee_df[safe_col(st.session_state.employee_df,"EmployeeCode")==emp_del]
                nm  = safe_col(row,"EmployeeName").iloc[0] if not row.empty else emp_del
                st.markdown(f"<div class='store-row'><div class='store-av av-r'>👤</div><div><div class='s-nm'>{nm}</div><div class='s-mt'>{emp_del}</div></div></div>", unsafe_allow_html=True)
                if st.button("🗑  Confirm Removal", type="primary"):
                    st.session_state.employee_df = st.session_state.employee_df[safe_col(st.session_state.employee_df,"EmployeeCode")!=emp_del]
                    if save_to_supabase("employee_master", st.session_state.employee_df):
                        st.success(f"✅ {nm} ({emp_del}) removed."); st.rerun()

    # ── Stores ────────────────────────────────────────────
    elif page == "Stores":
        page_hdr("Manage Stores 🏪","Add, view, or remove stores from the master list")
        tab1, tab2, tab3 = st.tabs(["  👁  View All  ","  ➕  Add Store  ","  🗑  Remove  "])

        with tab1:
            if not st.session_state.gst_df.empty:
                cities = ["All Cities"] + sorted(safe_col(st.session_state.gst_df,"City").dropna().unique().tolist())
                cf = st.selectbox("Filter by city", cities)
                df_s = st.session_state.gst_df if cf=="All Cities" else \
                    st.session_state.gst_df[safe_col(st.session_state.gst_df,"City")==cf]
                st.markdown(f"<p style='font-size:13px;color:#9ca3af;margin-bottom:8px;'>{len(df_s)} stores shown</p>", unsafe_allow_html=True)
                st.dataframe(df_s, use_container_width=True, hide_index=True)
            else:
                empty("🏪","No stores yet","Add stores using the Add Store tab.")

        with tab2:
            info_box("GST number must be a valid 15-character GSTIN. Format: <b>22AAAAA0000A1Z5</b>")
            with st.form("add_store", clear_on_submit=True):
                c1,c2 = st.columns(2)
                with c1:
                    sname = st.text_input("Store Name *",  placeholder="e.g. Reliance Fresh")
                    gstno = st.text_input("GST Number *",  max_chars=15, placeholder="22AAAAA0000A1Z5")
                with c2:
                    city    = st.text_input("City *", placeholder="e.g. Lucknow")
                    eopts   = safe_col(st.session_state.employee_df,"EmployeeCode").unique().tolist() or ["—"]
                    emp_sel = st.selectbox("Assign to Employee *", eopts)
                if st.form_submit_button("➕  Add Store", type="primary", use_container_width=True):
                    gc = gstno.strip().upper()
                    if not sname or not gc or not city:
                        st.error("⚠️ All fields are required.")
                    elif not is_valid_gstin(gc):
                        st.error("⚠️ Invalid GSTIN format. Example: 22AAAAA0000A1Z5")
                    elif safe_col(st.session_state.gst_df,"GSTNumber").astype(str).str.upper().eq(gc).any():
                        st.error(f"⚠️ GST number **{gc}** already exists in the system.")
                    else:
                        nid = f"S{len(st.session_state.gst_df)+1:05d}"
                        ns  = pd.DataFrame([{"StoreID":nid,"StoreName":sname.strip().title(),"GSTNumber":gc,"City":city.strip().title(),"EmployeeCode":emp_sel}])
                        st.session_state.gst_df = pd.concat([st.session_state.gst_df,ns],ignore_index=True)
                        if save_to_supabase("gst_master", st.session_state.gst_df):
                            st.success(f"✅ **{sname.strip().title()}** added and assigned to **{emp_sel}**!"); st.rerun()

        with tab3:
            if st.session_state.gst_df.empty:
                empty("🏪","No stores to remove","")
            else:
                warn_box("Removing a store deletes it from the master list. Existing plans are not affected.")
                sdel = st.selectbox("Choose store to remove", safe_col(st.session_state.gst_df,"StoreID").unique())
                row  = st.session_state.gst_df[safe_col(st.session_state.gst_df,"StoreID")==sdel]
                snm  = safe_col(row,"StoreName").iloc[0] if not row.empty else sdel
                st.markdown(f"<div class='store-row'><div class='store-av av-r'>🏪</div><div><div class='s-nm'>{snm}</div><div class='s-mt'>{sdel}</div></div></div>", unsafe_allow_html=True)
                if st.button("🗑  Confirm Removal", type="primary"):
                    st.session_state.gst_df = st.session_state.gst_df[safe_col(st.session_state.gst_df,"StoreID")!=sdel]
                    if save_to_supabase("gst_master", st.session_state.gst_df):
                        st.success(f"✅ {snm} removed."); st.rerun()

    # ── View Plans ────────────────────────────────────────
    elif page == "View Plans":
        page_hdr("View Plans 📋","Browse and filter all employee beat plans")

        with st.expander("🔍  Filter Plans", expanded=True):
            c1,c2,c3 = st.columns(3)
            with c1: femp  = st.selectbox("Employee",["All"]+list(safe_col(st.session_state.planned_df,"EmployeeName").dropna().unique()))
            with c2: fcity = st.selectbox("City",["All"]+list(safe_col(st.session_state.planned_df,"City").dropna().unique()))
            with c3: drange= st.date_input("Date Range", value=(date.today()-timedelta(days=30), date.today()))

        fp = st.session_state.planned_df.copy()
        if femp !="All" and "EmployeeName" in fp.columns: fp=fp[fp["EmployeeName"]==femp]
        if fcity!="All" and "City"         in fp.columns: fp=fp[fp["City"]==fcity]
        if isinstance(drange,(list,tuple)) and len(drange)==2 and "VisitDate" in fp.columns:
            fp=fp[(fp["VisitDate"]>=drange[0])&(fp["VisitDate"]<=drange[1])]

        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Plans Found",  len(fp))
        c2.metric("Employees",    safe_col(fp,"EmployeeName").nunique())
        c3.metric("Cities",       safe_col(fp,"City").nunique())
        c4.metric("Stores",       safe_col(fp,"Store").nunique())

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        if not fp.empty:
            st.dataframe(fp.sort_values("VisitDate",ascending=False) if "VisitDate" in fp.columns else fp, use_container_width=True, hide_index=True)
            download_btn(fp,"admin_dl","Beat_Plan_Admin")
        else:
            empty("📋","No plans match your filters","Try adjusting the filters above.")

    # ── Refresh ───────────────────────────────────────────
    elif page == "Refresh":
        page_hdr("Sync Data 🔄","Pull the latest records from Supabase")
        info_box("This refreshes <b>all tables</b>: Employees, Stores, Plans and Admin. Use after making changes in Supabase directly.")
        c1,_ = st.columns([1,2])
        with c1:
            if st.button("🔄  Refresh Now", type="primary", use_container_width=True):
                with st.spinner("Syncing from Supabase…"):
                    st.session_state.employee_df = load_from_supabase("employee_master", EMP_COLS)
                    st.session_state.gst_df      = load_from_supabase("gst_master",      GST_COLS)
                    st.session_state.planned_df  = load_from_supabase("planned_visits",  PLAN_COLS)
                    st.session_state.admin_df    = load_from_supabase("admin_master",    ADMIN_COLS)
                st.success("✅ All data refreshed successfully!"); st.rerun()

# ====================== EMPLOYEE PAGES ======================
else:
    my_stores = st.session_state.gst_df[
        safe_col(st.session_state.gst_df,"EmployeeCode").astype(str)==str(emp_code)
    ] if not st.session_state.gst_df.empty else pd.DataFrame(columns=GST_COLS)

    my_plans = st.session_state.planned_df[
        safe_col(st.session_state.planned_df,"EmployeeCode").astype(str)==str(emp_code)
    ]

    # ── Dashboard ─────────────────────────────────────────
    if page == "Dashboard":
        first = emp_name.split()[0]
        hr    = date.today().strftime("%H")
        greet = "Good morning" if int(hr)<12 else "Good afternoon" if int(hr)<17 else "Good evening"
        page_hdr(f"{greet}, {first}! 👋",
                 f"{date.today().strftime('%A, %d %B %Y')}  ·  Here's your field dashboard")

        today_plans = my_plans[my_plans["VisitDate"]==date.today()] if "VisitDate" in my_plans.columns else pd.DataFrame()
        this_month  = my_plans[pd.to_datetime(safe_col(my_plans,"VisitDate"),errors="coerce").dt.month==date.today().month] \
            if "VisitDate" in my_plans.columns else pd.DataFrame()

        stat_cards([
            ("linear-gradient(90deg,#4f46e5,#7c3aed)","#eef2ff","🏪",
             len(my_stores),f"My Stores",f"Across {safe_col(my_stores,'City').nunique()} cities","#4f46e5"),
            ("linear-gradient(90deg,#06b6d4,#0284c7)","#ecfeff","📋",
             len(my_plans),"All Plans","All time total","#0891b2"),
            ("linear-gradient(90deg,#f59e0b,#d97706)","#fffbeb","📅",
             len(this_month),"This Month",date.today().strftime("%B %Y"),"#d97706"),
            ("linear-gradient(90deg,#10b981,#059669)","#d1fae5","📍",
             len(today_plans),"Today","Max 10 stores/day","#059669"),
        ])

        # Quick actions
        st.markdown("<div class='qa-row'>", unsafe_allow_html=True)
        st.markdown("""
        <div class="qa-row">
            <div class="qa-card">
                <div class="qa-icon" style="background:#eef2ff;">🎯</div>
                <div><div class="qa-title">New Beat Plan</div>
                <div class="qa-desc">Plan today's store visits</div></div>
            </div>
            <div class="qa-card">
                <div class="qa-icon" style="background:#ecfeff;">📅</div>
                <div><div class="qa-title">My Plans</div>
                <div class="qa-desc">All scheduled visits</div></div>
            </div>
            <div class="qa-card">
                <div class="qa-icon" style="background:#d1fae5;">➕</div>
                <div><div class="qa-title">Add Store</div>
                <div class="qa-desc">Request a new store</div></div>
            </div>
        </div>""", unsafe_allow_html=True)
        qa1,qa2,qa3 = st.columns(3)
        with qa1:
            if st.button("Open Beat Plan →", key="qa1", use_container_width=True): go("Beat Plan")
        with qa2:
            if st.button("View My Plans →",  key="qa2", use_container_width=True): go("My Plans")
        with qa3:
            if st.button("Add Store →",      key="qa3", use_container_width=True): go("Add Store")

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        # Two column: today + upcoming
        cl, cr = st.columns(2)

        with cl:
            pc    = len(today_plans)
            color = prog_color(pc)
            pct   = min(pc*10,100)
            st.markdown(f"""
            <div class="card">
                <div class="card-hdr">
                    <div class="card-hdr-icon" style="background:#eef2ff;">📍</div>
                    Today's Plan
                    <span class="card-pill"
                        style="background:{'#fef2f2' if pc>=10 else '#eef2ff'};
                               color:{'#b91c1c' if pc>=10 else '#4338ca'};">
                        {pc}/10
                    </span>
                </div>
                <div class="prog-wrap">
                    <div class="prog-row">
                        <span class="prog-lbl">Progress</span>
                        <span class="prog-num" style="color:{color};">{pc} of 10 stores</span>
                    </div>
                    <div class="prog-track">
                        <div class="prog-fill" style="width:{pct}%;background:{color};"></div>
                    </div>
                    <div class="prog-hint">
                        {"🚫 Limit reached for today" if pc>=10 else f"✅ {10-pc} more store(s) can be added"}
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

            if not today_plans.empty:
                for _, row in today_plans.iterrows():
                    st.markdown(f"""
                    <div class="store-row">
                        <div class="store-av av-g">✓</div>
                        <div style="flex:1;min-width:0;">
                            <div class="s-nm">{row.get('Store','—')}</div>
                            <div class="s-mt">{row.get('City','—')}</div>
                        </div>
                        <span class="bdg bdg-g">Planned</span>
                    </div>""", unsafe_allow_html=True)
            else:
                empty("📍","No stores planned today",
                      "Tap 'Open Beat Plan' above to start planning.")

        with cr:
            st.markdown("""
            <div class="card">
                <div class="card-hdr">
                    <div class="card-hdr-icon" style="background:#ecfeff;">📆</div>
                    Upcoming Visits
                </div>
            </div>""", unsafe_allow_html=True)

            if "VisitDate" in st.session_state.planned_df.columns:
                upcoming = st.session_state.planned_df[
                    (safe_col(st.session_state.planned_df,"EmployeeCode").astype(str)==str(emp_code)) &
                    (st.session_state.planned_df["VisitDate"] >= date.today())
                ].sort_values("VisitDate")
                if upcoming.empty:
                    empty("📆","No upcoming visits","Plan your visits in the Beat Plan section.")
                else:
                    for vd in sorted(upcoming["VisitDate"].unique())[:4]:
                        pl     = upcoming[upcoming["VisitDate"]==vd]
                        bc     = "tod" if vd==date.today() else "fut"
                        cities = ", ".join(sorted(safe_col(pl,"City").dropna().unique().tolist()))
                        stores = safe_col(pl,"Store").dropna().unique().tolist()
                        pills  = "".join(f"<span class='tl-pill'>{s}</span>" for s in stores[:3])
                        if len(stores)>3: pills += f"<span class='tl-pill'>+{len(stores)-3}</span>"
                        st.markdown(f"""
                        <div class="tl-item">
                            <div class="tl-date {bc}">
                                <div class="tl-day">{vd.strftime('%d')}</div>
                                <div class="tl-mon">{vd.strftime('%b')}</div>
                            </div>
                            <div>
                                <div class="tl-title">{len(pl)} store(s)</div>
                                <div class="tl-sub">{cities}</div>
                                <div class="tl-pills">{pills}</div>
                            </div>
                        </div>""", unsafe_allow_html=True)

    # ── Beat Plan ─────────────────────────────────────────
    elif page == "Beat Plan":
        page_hdr("Beat Plan 🎯","Select a date, pick your cities, and add stores to your visit list")

        if my_stores.empty:
            st.markdown("""
            <div class="card">
                <div class="empty">
                    <div class="empty-icon">⚠️</div>
                    <div class="empty-title">No stores assigned to you</div>
                    <div class="empty-sub">Please contact your admin to assign stores to your account.</div>
                </div>
            </div>""", unsafe_allow_html=True)
            st.stop()

        c1,c2,c3 = st.columns([1,2,1])
        with c1:
            visit_date = st.date_input("📅 Visit Date", value=date.today(), key="bd",
                                       min_value=date.today()-timedelta(days=7))
        with c2:
            city_opts  = sorted(safe_col(my_stores,"City").dropna().unique().tolist())
            sel_cities = st.multiselect(
                f"🌍 Cities ({len(city_opts)} available, max 3)",
                city_opts, max_selections=3, key="cms")
        with c3:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            if st.button("🔍  Filter", use_container_width=True):
                st.session_state.selected_cities = sel_cities; st.rerun()

        daily = my_plans[my_plans["VisitDate"]==visit_date] if "VisitDate" in my_plans.columns else pd.DataFrame(columns=PLAN_COLS)
        pc    = len(daily)
        color = prog_color(pc)
        pct   = min(pc*10,100)

        st.markdown(f"""
        <div class="card">
            <div class="card-hdr">
                <div class="card-hdr-icon" style="background:#eef2ff;">📊</div>
                {visit_date.strftime('%d %b %Y')} — Daily Progress
                <span class="card-pill"
                    style="background:{'#fef2f2' if pc>=10 else '#eef2ff'};
                           color:{'#b91c1c' if pc>=10 else '#4338ca'};">
                    {pc} / 10
                </span>
            </div>
            <div class="prog-row">
                <span class="prog-lbl">
                    {"🚫 Limit reached — 10 stores max per day" if pc>=10 else f"✅ {10-pc} more store(s) can be added"}
                </span>
                <span class="prog-num" style="color:{color};">{pct}%</span>
            </div>
            <div class="prog-track">
                <div class="prog-fill" style="width:{pct}%;background:{color};"></div>
            </div>
        </div>""", unsafe_allow_html=True)

        if not daily.empty:
            with st.expander(f"📋 Already planned for {visit_date}  ({pc} store(s))"):
                cols = [c for c in ["Store","City","GSTNumber","StoreID"] if c in daily.columns]
                st.dataframe(daily[cols], use_container_width=True, hide_index=True)

        if pc < 10:
            show_cities = st.session_state.selected_cities or safe_col(my_stores,"City").unique().tolist()
            avail = my_stores[
                safe_col(my_stores,"City").isin(show_cities) &
                ~safe_col(my_stores,"StoreID").isin(safe_col(daily,"StoreID").tolist())
            ]

            st.markdown(
                f"<div class='sec-hd'>🏪 Available Stores "
                f"<span class='sec-ct'>{len(avail)} stores</span></div>",
                unsafe_allow_html=True)

            if avail.empty:
                empty("🎉","All done!","You've planned all available stores for the selected cities.")
            else:
                for idx, row in avail.iterrows():
                    c1, c2 = st.columns([6,1])
                    with c1:
                        st.markdown(f"""
                        <div class="store-row">
                            <div class="store-av av-i">🏪</div>
                            <div style="flex:1;min-width:0;">
                                <div class="s-nm">{row.get('StoreName','—')}</div>
                                <div class="s-mt">{row.get('City','—')} &nbsp;·&nbsp; {row.get('GSTNumber','—')}</div>
                            </div>
                            <span class="bdg bdg-g">Available</span>
                        </div>""", unsafe_allow_html=True)
                    with c2:
                        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
                        if st.button("➕", key=f"add_{idx}_{visit_date}", use_container_width=True):
                            nr = pd.DataFrame([{
                                "EmployeeCode":emp_code,"EmployeeName":emp_name,
                                "City":row.get("City",""),"Store":row.get("StoreName",""),
                                "StoreID":row.get("StoreID",""),"GSTNumber":row.get("GSTNumber",""),
                                "VisitDate":visit_date
                            }])
                            st.session_state.planned_df = pd.concat([st.session_state.planned_df,nr],ignore_index=True)
                            if save_to_supabase("planned_visits", st.session_state.planned_df):
                                st.success(f"✅ {row.get('StoreName','')} added for {visit_date}!"); st.rerun()

        st.markdown("---")
        download_btn(my_plans,"emp_dl",f"Beat_Plan_{emp_code}")

    # ── My Plans ──────────────────────────────────────────
    elif page == "My Plans":
        page_hdr("My Plans 📅","All your scheduled store visits")

        if my_plans.empty:
            empty("📅","No plans yet","Go to Beat Plan to schedule your first store visit.")
        else:
            this_month = my_plans[pd.to_datetime(safe_col(my_plans,"VisitDate"),errors="coerce").dt.month==date.today().month] \
                if "VisitDate" in my_plans.columns else pd.DataFrame()
            stat_cards([
                ("linear-gradient(90deg,#4f46e5,#7c3aed)","#eef2ff","📋",
                 len(my_plans),"Total Plans","All time","#4f46e5"),
                ("linear-gradient(90deg,#06b6d4,#0284c7)","#ecfeff","📍",
                 safe_col(my_plans,"City").nunique(),"Cities Covered","Unique","#0891b2"),
                ("linear-gradient(90deg,#f59e0b,#d97706)","#fffbeb","📅",
                 len(safe_col(my_plans,"VisitDate").unique()),"Unique Dates","Days planned","#d97706"),
                ("linear-gradient(90deg,#10b981,#059669)","#d1fae5","🏪",
                 safe_col(my_plans,"Store").nunique(),"Unique Stores","Total","#059669"),
            ])

            with st.expander("🔍  Filter my plans", expanded=False):
                c1,c2 = st.columns(2)
                with c1: fc = st.selectbox("City",["All"]+sorted(safe_col(my_plans,"City").dropna().unique().tolist()))
                with c2: fd = st.date_input("From date", value=date.today()-timedelta(days=30), key="mpd")

            df_mp = my_plans.copy()
            if fc!="All" and "City" in df_mp.columns: df_mp=df_mp[df_mp["City"]==fc]
            if "VisitDate" in df_mp.columns: df_mp=df_mp[df_mp["VisitDate"]>=fd]

            st.dataframe(
                df_mp.sort_values("VisitDate",ascending=False) if "VisitDate" in df_mp.columns else df_mp,
                use_container_width=True, hide_index=True)
            download_btn(df_mp,"my_dl",f"My_Plans_{emp_code}")

    # ── Upcoming ──────────────────────────────────────────
    elif page == "Upcoming":
        page_hdr("Upcoming Visits 📆","Your planned visits from today onwards")

        if "VisitDate" not in st.session_state.planned_df.columns:
            empty("📆","No upcoming visits","Plan visits from the Beat Plan section.")
        else:
            upcoming = st.session_state.planned_df[
                (safe_col(st.session_state.planned_df,"EmployeeCode").astype(str)==str(emp_code)) &
                (st.session_state.planned_df["VisitDate"] >= date.today())
            ].sort_values("VisitDate")

            if upcoming.empty:
                empty("📆","No upcoming visits","Plan visits from the Beat Plan section.")
            else:
                total_days   = len(upcoming["VisitDate"].unique())
                total_stores = len(upcoming)
                st.markdown(f"<p style='font-size:13.5px;color:#6b7280;margin-bottom:12px;'>📅 <b>{total_stores} visits</b> across <b>{total_days} days</b></p>", unsafe_allow_html=True)

                for vd in sorted(upcoming["VisitDate"].unique()):
                    pl     = upcoming[upcoming["VisitDate"]==vd]
                    bc     = "tod" if vd==date.today() else "fut"
                    cities = ", ".join(sorted(safe_col(pl,"City").dropna().unique().tolist()))
                    stores = safe_col(pl,"Store").dropna().unique().tolist()
                    pills  = "".join(f"<span class='tl-pill'>{s}</span>" for s in stores[:5])
                    if len(stores)>5: pills += f"<span class='tl-pill'>+{len(stores)-5} more</span>"
                    today_tag = "<span class='bdg bdg-p' style='margin-left:auto;'>Today</span>" if vd==date.today() else ""
                    st.markdown(f"""
                    <div class="tl-item">
                        <div class="tl-date {bc}">
                            <div class="tl-day">{vd.strftime('%d')}</div>
                            <div class="tl-mon">{vd.strftime('%b')}</div>
                        </div>
                        <div style="flex:1;min-width:0;">
                            <div class="tl-title">{len(pl)} store(s) · {vd.strftime('%A')}</div>
                            <div class="tl-sub">{cities}</div>
                            <div class="tl-pills">{pills}</div>
                        </div>
                        {today_tag}
                    </div>""", unsafe_allow_html=True)

    # ── Analytics ─────────────────────────────────────────
    elif page == "Analytics":
        page_hdr("Analytics 📈","Your personal performance insights")

        if my_plans.empty:
            empty("📈","No data yet","Your analytics appear once you start planning visits.")
        else:
            this_month = my_plans[pd.to_datetime(safe_col(my_plans,"VisitDate"),errors="coerce").dt.month==date.today().month] \
                if "VisitDate" in my_plans.columns else pd.DataFrame()
            stat_cards([
                ("linear-gradient(90deg,#4f46e5,#7c3aed)","#eef2ff","📋",
                 len(my_plans),"Total Visits","All time","#4f46e5"),
                ("linear-gradient(90deg,#06b6d4,#0284c7)","#ecfeff","📍",
                 safe_col(my_plans,"City").nunique(),"Cities","Covered","#0891b2"),
                ("linear-gradient(90deg,#f59e0b,#d97706)","#fffbeb","🏪",
                 safe_col(my_plans,"Store").nunique(),"Unique Stores","Visited","#d97706"),
                ("linear-gradient(90deg,#10b981,#059669)","#d1fae5","📅",
                 len(this_month),"This Month",date.today().strftime("%B"),"#059669"),
            ])

            st.markdown("---")
            c1,c2 = st.columns(2)
            with c1:
                st.markdown("<div class='sec-hd'>Visits by City</div>", unsafe_allow_html=True)
                if "City" in my_plans.columns:
                    cd = my_plans.groupby("City").size().reset_index(name="Visits").set_index("City")
                    st.bar_chart(cd, color="#4f46e5")
            with c2:
                st.markdown("<div class='sec-hd'>Monthly Trend</div>", unsafe_allow_html=True)
                if "VisitDate" in my_plans.columns:
                    tmp = my_plans.copy()
                    tmp["Month"] = pd.to_datetime(tmp["VisitDate"],errors="coerce").dt.to_period("M").astype(str)
                    st.line_chart(tmp.groupby("Month").size(), color="#06b6d4")

            st.markdown("<div class='sec-hd'>Most Visited Stores <span class='sec-ct'>Top 10</span></div>", unsafe_allow_html=True)
            if "Store" in my_plans.columns:
                top = my_plans.groupby("Store").agg(
                    Visits=("Store","count"), City=("City","first")
                ).reset_index().sort_values("Visits",ascending=False).head(10)
                st.dataframe(top, use_container_width=True, hide_index=True)

    # ── Add Store ─────────────────────────────────────────
    elif page == "Add Store":
        page_hdr("Add New Store ➕","Request a store to be added to your territory")
        info_box("Make sure you have the correct GSTIN before submitting. "
                 "Format: <b>22AAAAA0000A1Z5</b> (15 characters).")

        with st.form("store_req", clear_on_submit=True):
            c1,c2 = st.columns(2)
            with c1:
                sname = st.text_input("Store Name *",  placeholder="e.g. Reliance Fresh, Sector 12")
                city  = st.text_input("City *",        placeholder="e.g. Lucknow")
            with c2:
                gst = st.text_input("GST Number *", max_chars=15, placeholder="22AAAAA0000A1Z5")
                st.text_area("Remarks (optional)", height=92,
                             placeholder="Location details, directions, any notes for admin…")
            if st.form_submit_button("➕  Add to My Territory", type="primary", use_container_width=True):
                gc = gst.strip().upper()
                if not sname or not city or not gc:
                    st.error("⚠️ Store name, city, and GST number are required.")
                elif not is_valid_gstin(gc):
                    st.error("⚠️ Invalid GSTIN. Please check the format: 22AAAAA0000A1Z5")
                elif safe_col(st.session_state.gst_df,"GSTNumber").astype(str).str.upper().eq(gc).any():
                    st.error(f"⚠️ GSTIN **{gc}** already exists in the system.")
                else:
                    nid = f"S{len(st.session_state.gst_df)+1:05d}"
                    ns  = pd.DataFrame([{"StoreID":nid,"StoreName":sname.strip().title(),"GSTNumber":gc,"City":city.strip().title(),"EmployeeCode":emp_code}])
                    st.session_state.gst_df = pd.concat([st.session_state.gst_df,ns],ignore_index=True)
                    if save_to_supabase("gst_master", st.session_state.gst_df):
                        st.success(f"✅ **{sname.strip().title()}** added to your territory in {city.strip().title()}!"); st.rerun()

# ====================== FOOTER ======================
st.markdown("---")
st.markdown(
    "<div style='text-align:center;font-size:12px;color:#c4c9d9;padding:4px 0'>"
    "Beat Plan Pro &nbsp;·&nbsp; 2026 &nbsp;·&nbsp; Built by Bipin Pandey"
    "</div>", unsafe_allow_html=True)
