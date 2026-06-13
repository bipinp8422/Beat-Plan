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
    layout="centered",
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

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* ── Mobile-first base ── */
.stApp { background: #f4f6fb !important; }
.block-container {
    padding: 0 0 100px 0 !important;
    max-width: 480px !important;
    margin: 0 auto !important;
}
#MainMenu, footer, header { visibility: hidden; }
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }

/* ── TOP HEADER BAR ── */
.app-header {
    position: sticky; top: 0; z-index: 999;
    background: #fff;
    border-bottom: 1px solid #e8eaf0;
    padding: 14px 18px 10px;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.header-logo {
    display: flex; align-items: center; gap: 8px;
    font-size: 16px; font-weight: 800; color: #18181b; letter-spacing: -0.3px;
}
.header-logo-icon {
    width: 32px; height: 32px; border-radius: 9px;
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    display: flex; align-items: center; justify-content: center; font-size: 16px;
}
.header-right { display: flex; align-items: center; gap: 8px; }
.header-avatar {
    width: 34px; height: 34px; border-radius: 50%;
    background: linear-gradient(135deg, #4f46e5, #06b6d4);
    color: #fff; font-size: 12px; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
}

/* ── PAGE CONTENT ── */
.page-content { padding: 16px 16px 0; }

/* ── PAGE TITLE ── */
.page-title {
    font-size: 22px; font-weight: 800; color: #18181b;
    letter-spacing: -0.5px; margin-bottom: 2px;
}
.page-sub { font-size: 13px; color: #9ca3af; margin-bottom: 16px; }

/* ── GREETING ── */
.greeting {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    border-radius: 18px; padding: 20px 20px 18px;
    color: #fff; margin-bottom: 16px;
}
.greeting-hi   { font-size: 20px; font-weight: 800; margin-bottom: 4px; }
.greeting-sub  { font-size: 13px; opacity: 0.8; }
.greeting-date { font-size: 12px; opacity: 0.65; margin-top: 8px; }

/* ── STAT CARDS ── */
.stat-row {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 10px; margin-bottom: 16px;
}
.stat-card {
    background: #fff; border: 1px solid #e8eaf0;
    border-radius: 16px; padding: 16px 16px 12px;
    position: relative; overflow: hidden;
}
.stat-top { width: 100%; height: 3px; position: absolute; top: 0; left: 0; }
.stat-icon { font-size: 22px; margin-bottom: 8px; }
.stat-val  { font-size: 26px; font-weight: 800; color: #18181b; letter-spacing: -1px; line-height: 1; }
.stat-lbl  { font-size: 12px; color: #9ca3af; margin-top: 3px; font-weight: 500; }
.stat-foot { font-size: 11px; font-weight: 600; margin-top: 8px; }

/* ── SECTION HEADING ── */
.sec-hd {
    font-size: 15px; font-weight: 700; color: #18181b;
    margin: 20px 0 10px; display: flex; align-items: center; gap: 7px;
}
.sec-ct {
    font-size: 11px; background: #f0f2f8; color: #6b7280;
    padding: 2px 8px; border-radius: 20px; font-weight: 600;
}

/* ── CARD ── */
.card {
    background: #fff; border: 1px solid #e8eaf0;
    border-radius: 16px; padding: 16px 16px 12px;
    margin-bottom: 10px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.04);
}
.card-hdr {
    display: flex; align-items: center; gap: 8px;
    font-size: 14px; font-weight: 700; color: #18181b;
    padding-bottom: 10px; margin-bottom: 12px;
    border-bottom: 1px solid #f4f6fb;
}
.card-hdr-icon {
    width: 28px; height: 28px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center; font-size: 14px;
}
.card-pill {
    font-size: 11px; padding: 3px 9px;
    border-radius: 20px; font-weight: 600; margin-left: auto;
}

/* ── PROGRESS ── */
.prog-row  { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.prog-lbl  { font-size: 13px; font-weight: 600; color: #374151; }
.prog-num  { font-size: 13px; font-weight: 700; }
.prog-track { height: 8px; background: #f0f2f8; border-radius: 99px; overflow: hidden; margin-bottom: 6px; }
.prog-fill  { height: 100%; border-radius: 99px; }
.prog-hint  { font-size: 12px; color: #9ca3af; }

/* ── STORE ITEM ── */
.store-item {
    display: flex; align-items: center; gap: 12px;
    padding: 12px 14px; border-radius: 14px;
    background: #f9fafb; border: 1px solid #f0f2f8;
    margin-bottom: 8px; transition: all .15s;
}
.store-item:hover { background: #f0f2f8; }
.store-av {
    width: 40px; height: 40px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; flex-shrink: 0;
}
.av-i { background: #eef2ff; }
.av-g { background: #f0fdf4; }
.av-r { background: #fef2f2; }
.av-a { background: #fffbeb; }
.s-nm { font-size: 13.5px; font-weight: 600; color: #18181b; }
.s-mt { font-size: 12px; color: #9ca3af; margin-top: 2px; }

/* ── BADGES ── */
.bdg { font-size: 11px; padding: 4px 10px; border-radius: 20px; font-weight: 600; white-space: nowrap; flex-shrink: 0; }
.bdg-g  { background: #dcfce7; color: #15803d; }
.bdg-r  { background: #fee2e2; color: #b91c1c; }
.bdg-a  { background: #fef9c3; color: #854d0e; }
.bdg-p  { background: #ede9fe; color: #6d28d9; }
.bdg-b  { background: #dbeafe; color: #1d4ed8; }

/* ── TIMELINE ── */
.tl-item {
    display: flex; gap: 12px; align-items: flex-start;
    padding: 12px 14px; border-radius: 14px;
    background: #f9fafb; border: 1px solid #f0f2f8;
    margin-bottom: 8px;
}
.tl-date {
    width: 44px; flex-shrink: 0; text-align: center; border-radius: 12px; padding: 7px 3px;
}
.tl-date.tod {
    background: linear-gradient(135deg,#4f46e5,#7c3aed);
    box-shadow: 0 3px 10px rgba(79,70,229,.28);
}
.tl-date.fut { background: #fff; border: 1px solid #e8eaf0; }
.tl-day { font-size: 19px; font-weight: 800; line-height: 1; }
.tl-mon { font-size: 9px; text-transform: uppercase; letter-spacing: .06em; margin-top: 2px; }
.tl-date.tod .tl-day,.tl-date.tod .tl-mon { color: #fff; }
.tl-date.fut .tl-day { color: #18181b; }
.tl-date.fut .tl-mon { color: #9ca3af; }
.tl-title { font-size: 13.5px; font-weight: 700; color: #18181b; margin-bottom: 2px; }
.tl-sub   { font-size: 12px; color: #9ca3af; margin-bottom: 5px; }
.tl-pills { display: flex; flex-wrap: wrap; gap: 4px; }
.tl-pill  { font-size: 11px; background: #fff; border: 1px solid #e8eaf0; color: #4b5563; padding: 2px 7px; border-radius: 20px; }

/* ── QUICK ACTION GRID ── */
.qa-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 16px; }
.qa-card {
    background: #fff; border: 1px solid #e8eaf0;
    border-radius: 16px; padding: 16px 14px;
    display: flex; flex-direction: column; align-items: flex-start; gap: 8px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.04); transition: all .15s; cursor: pointer;
}
.qa-card:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
.qa-icon { width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
.qa-label { font-size: 13px; font-weight: 700; color: #18181b; }
.qa-desc  { font-size: 11.5px; color: #9ca3af; }

/* ── BOTTOM NAV ── */
.bottom-nav {
    position: fixed; bottom: 0; left: 0; right: 0; z-index: 999;
    background: #fff; border-top: 1px solid #e8eaf0;
    display: flex; justify-content: space-around; align-items: center;
    padding: 8px 0 12px;
    box-shadow: 0 -4px 20px rgba(0,0,0,0.08);
    max-width: 480px; margin: 0 auto;
}
.nav-item {
    display: flex; flex-direction: column; align-items: center; gap: 3px;
    font-size: 10px; font-weight: 500; color: #9ca3af;
    cursor: pointer; padding: 4px 12px; border-radius: 12px;
    transition: all .15s; flex: 1; text-align: center;
}
.nav-item.active { color: #4f46e5; }
.nav-item .nav-icon { font-size: 22px; line-height: 1; }
.nav-item.active .nav-icon { transform: scale(1.15); }

/* ── INFO / WARN BOXES ── */
.info-box {
    background: #eef2ff; border: 1px solid #c7d2fe;
    border-radius: 12px; padding: 12px 14px;
    font-size: 13px; color: #3730a3; margin-bottom: 14px;
    line-height: 1.6;
}
.warn-box {
    background: #fffbeb; border: 1px solid #fcd34d;
    border-radius: 12px; padding: 12px 14px;
    font-size: 13px; color: #92400e; margin-bottom: 14px;
    line-height: 1.6;
}
.success-box {
    background: #f0fdf4; border: 1px solid #86efac;
    border-radius: 12px; padding: 12px 14px;
    font-size: 13px; color: #15803d; margin-bottom: 14px;
    line-height: 1.6;
}

/* ── EMPTY STATE ── */
.empty { text-align: center; padding: 40px 20px; }
.empty-icon  { font-size: 44px; margin-bottom: 12px; }
.empty-title { font-size: 15px; font-weight: 700; color: #374151; margin-bottom: 4px; }
.empty-sub   { font-size: 13px; color: #9ca3af; line-height: 1.6; }

/* ── LOGIN ── */
.lg-wrap { max-width: 440px; margin: 0 auto; padding: 24px 18px; }
.lg-top  { text-align: center; margin-bottom: 28px; padding-top: 20px; }
.lg-icon {
    width: 68px; height: 68px; border-radius: 20px;
    background: linear-gradient(135deg,#4f46e5,#7c3aed);
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 32px; color: #fff; margin-bottom: 16px;
    box-shadow: 0 8px 24px rgba(79,70,229,.3);
}
.lg-title { font-size: 26px; font-weight: 800; color: #18181b; letter-spacing: -0.5px; }
.lg-sub   { font-size: 14px; color: #9ca3af; margin-top: 6px; }
.lg-card  {
    background: #fff; border: 1px solid #e8eaf0;
    border-radius: 20px; padding: 24px 22px;
    box-shadow: 0 8px 32px rgba(0,0,0,.07);
}
.lg-lbl { font-size: 13px; font-weight: 600; color: #374151; margin-bottom: 5px; }

/* ── STREAMLIT OVERRIDES ── */
/* Big tap-friendly buttons */
.stButton > button {
    border-radius: 14px !important; height: 52px !important;
    font-weight: 700 !important; font-size: 15px !important;
    background: #4f46e5 !important; color: #fff !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(79,70,229,.25) !important;
    transition: all .15s !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: #4338ca !important;
    box-shadow: 0 6px 20px rgba(79,70,229,.35) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: scale(0.98) !important; }

/* Inputs — large touch targets */
.stTextInput > div > div > input {
    border-radius: 12px !important; border: 1.5px solid #e8eaf0 !important;
    font-size: 16px !important; background: #fafbff !important;
    padding: 14px 16px !important; height: 52px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #4f46e5 !important; background: #fff !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,.1) !important;
}
.stTextInput > div > div > input::placeholder { color: #c4c9d9 !important; }
.stSelectbox > div > div {
    border-radius: 12px !important; border: 1.5px solid #e8eaf0 !important;
    background: #fafbff !important; min-height: 52px !important;
    font-size: 15px !important;
}
.stMultiSelect > div > div {
    border-radius: 12px !important; border: 1.5px solid #e8eaf0 !important;
    min-height: 52px !important; font-size: 15px !important;
}
.stDateInput > div > div > input {
    border-radius: 12px !important; border: 1.5px solid #e8eaf0 !important;
    height: 52px !important; font-size: 15px !important; padding: 14px 16px !important;
}
.stTextArea > div > div > textarea {
    border-radius: 12px !important; border: 1.5px solid #e8eaf0 !important;
    font-size: 15px !important; background: #fafbff !important;
    padding: 14px 16px !important;
}

/* Tabs — pill style */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px; background: #f0f2f8; border-radius: 14px;
    padding: 5px; border: none !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important; font-size: 13.5px !important;
    font-weight: 600 !important; padding: 10px 18px !important;
    color: #6b7280 !important; background: transparent !important; border: none !important;
}
.stTabs [aria-selected="true"] {
    background: #fff !important; color: #4f46e5 !important;
    font-weight: 700 !important; box-shadow: 0 2px 8px rgba(0,0,0,.08) !important;
}

/* DataFrames */
.stDataFrame { border-radius: 14px !important; border: 1px solid #e8eaf0 !important; overflow: hidden !important; }

/* Alerts */
.stAlert { border-radius: 14px !important; font-size: 14px !important; }

/* Download */
.stDownloadButton > button {
    background: #f9fafb !important; color: #374151 !important;
    border: 1.5px solid #e8eaf0 !important; border-radius: 14px !important;
    font-weight: 600 !important; box-shadow: none !important; height: 52px !important;
}
.stDownloadButton > button:hover { background: #f0f2f8 !important; transform: none !important; }

/* Expander */
.streamlit-expanderHeader {
    background: #f9fafb !important; border-radius: 12px !important;
    font-size: 14px !important; font-weight: 600 !important;
    border: 1px solid #e8eaf0 !important; color: #374151 !important;
    padding: 14px 16px !important;
}
hr { border-color: #e8eaf0 !important; margin: 16px 0 !important; }

/* Labels */
.stTextInput label, .stSelectbox label, .stMultiSelect label,
.stDateInput label, .stTextArea label {
    font-size: 13.5px !important; font-weight: 600 !important; color: #374151 !important;
}

/* Spinner */
.stSpinner { text-align: center; }

/* Metric override */
[data-testid="stMetric"] {
    background: #fff !important; border: 1px solid #e8eaf0 !important;
    border-radius: 14px !important; padding: 16px !important;
}
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
    except Exception as e: st.error(f"❌ {e}"); return False

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
        st.warning(f"⚠️ Could not load `{table}`: {e}")
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
        st.error(f"❌ Save failed: {e}"); return False

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

DEFAULTS = {"logged_in":False,"role":"","emp_code":"","emp_name":"","page":"Home","selected_cities":[]}
for k,v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

# ====================== UTILS ======================
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

def stat_cards_2col(items):
    html = "<div class='stat-row'>"
    for top, ico, val, lbl, foot, fc in items:
        html += f"""
        <div class="stat-card">
            <div class="stat-top" style="background:{top}"></div>
            <div class="stat-icon">{ico}</div>
            <div class="stat-val">{val}</div>
            <div class="stat-lbl">{lbl}</div>
            <div class="stat-foot" style="color:{fc};">{foot}</div>
        </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

def empty_state(icon, title, sub=""):
    st.markdown(f"""
    <div class="empty">
        <div class="empty-icon">{icon}</div>
        <div class="empty-title">{title}</div>
        <div class="empty-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

def info_box(msg):
    st.markdown(f'<div class="info-box">ℹ️  {msg}</div>', unsafe_allow_html=True)

def warn_box(msg):
    st.markdown(f'<div class="warn-box">⚠️  {msg}</div>', unsafe_allow_html=True)

def render_header(name, role):
    ini      = get_initials(name) if name else "??"
    role_lbl = "Admin" if role=="admin" else "Employee"
    st.markdown(f"""
    <div class="app-header">
        <div class="header-logo">
            <div class="header-logo-icon">🗺️</div>
            Beat Plan Pro
        </div>
        <div class="header-right">
            <div style="text-align:right;margin-right:4px;">
                <div style="font-size:12.5px;font-weight:600;color:#18181b;">{name}</div>
                <div style="font-size:10.5px;color:#9ca3af;">{role_lbl}</div>
            </div>
            <div class="header-avatar">{ini}</div>
        </div>
    </div>""", unsafe_allow_html=True)

def bottom_nav_employee(page):
    items = [
        ("Home","🏠","Home"),
        ("Beat Plan","🎯","Plan"),
        ("My Plans","📅","Plans"),
        ("Upcoming","📆","Upcoming"),
        ("Analytics","📈","Stats"),
    ]
    html = "<div class='bottom-nav'>"
    for p, icon, label in items:
        cls = "nav-item active" if page==p else "nav-item"
        html += f'<div class="{cls}"><div class="nav-icon">{icon}</div>{label}</div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    # Real functional buttons (hidden by CSS overlap with HTML nav)
    st.markdown("""
    <style>
    .bottom-nav-btns {
        position: fixed; bottom: 0; left: 0; right: 0; z-index: 1000;
        max-width: 480px; margin: 0 auto;
        display: flex; height: 70px;
    }
    .bottom-nav-btns .stButton > button {
        border-radius: 0 !important; height: 70px !important;
        background: transparent !important; color: transparent !important;
        box-shadow: none !important; border: none !important;
        font-size: 1px !important;
    }
    </style>
    <div class="bottom-nav-btns">
    """, unsafe_allow_html=True)
    cols = st.columns(5)
    pages = ["Home","Beat Plan","My Plans","Upcoming","Analytics"]
    for i, (col, pg) in enumerate(zip(cols, pages)):
        with col:
            if st.button(".", key=f"bnav_{pg}", use_container_width=True):
                go(pg)
    st.markdown("</div>", unsafe_allow_html=True)

def bottom_nav_admin(page):
    items = [
        ("Home","🏠","Home"),
        ("Employees","👥","Team"),
        ("Stores","🏪","Stores"),
        ("View Plans","📋","Plans"),
        ("Refresh","🔄","Sync"),
    ]
    html = "<div class='bottom-nav'>"
    for p, icon, label in items:
        cls = "nav-item active" if page==p else "nav-item"
        html += f'<div class="{cls}"><div class="nav-icon">{icon}</div>{label}</div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    st.markdown("""
    <style>
    .bottom-nav-btns {
        position: fixed; bottom: 0; left: 0; right: 0; z-index: 1000;
        max-width: 480px; margin: 0 auto;
        display: flex; height: 70px;
    }
    .bottom-nav-btns .stButton > button {
        border-radius: 0 !important; height: 70px !important;
        background: transparent !important; color: transparent !important;
        box-shadow: none !important; border: none !important;
        font-size: 1px !important;
    }
    </style>
    <div class="bottom-nav-btns">
    """, unsafe_allow_html=True)
    cols = st.columns(5)
    pages = ["Home","Employees","Stores","View Plans","Refresh"]
    for i, (col, pg) in enumerate(zip(cols, pages)):
        with col:
            if st.button(".", key=f"bnav_{pg}", use_container_width=True):
                go(pg)
    st.markdown("</div>", unsafe_allow_html=True)

# ====================== LOGIN ======================
if not st.session_state.logged_in:
    st.markdown("<div class='lg-wrap'>", unsafe_allow_html=True)
    st.markdown("""
        <div class="lg-top">
            <div class="lg-icon">🗺️</div>
            <div class="lg-title">Beat Plan Pro</div>
            <div class="lg-sub">Smart store visit planning</div>
        </div>""", unsafe_allow_html=True)

    login_type = st.radio("Role", ["🛡️  Admin","👷  Employee"],
                          horizontal=True, label_visibility="collapsed")
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    is_admin = "Admin" in login_type

    with st.container():
        if is_admin:
            st.markdown("<div class='lg-lbl'>👤  Username</div>", unsafe_allow_html=True)
            user = st.text_input("u", placeholder="Admin username",
                                 key="au", label_visibility="collapsed")
            st.markdown("<div class='lg-lbl'>🔒  Password</div>", unsafe_allow_html=True)
            pwd  = st.text_input("p", type="password", placeholder="Password",
                                 key="ap", label_visibility="collapsed")
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            if st.button("Sign in as Admin →", type="primary", use_container_width=True):
                if not user or not pwd:
                    st.error("Please enter both username and password.")
                else:
                    df = st.session_state.admin_df
                    ok = (
                        (df["Username"].astype(str).str.strip()==user.strip()) &
                        (df["Password"].astype(str).str.strip()==pwd.strip())
                    ) if "Username" in df.columns else pd.Series([False])
                    if ok.any():
                        st.session_state.update(logged_in=True,role="admin",
                                                emp_name="Admin",page="Home")
                        st.rerun()
                    else:
                        st.error(f"❌ Incorrect credentials.")
        else:
            st.markdown("<div class='lg-lbl'>🪪  Employee Code</div>", unsafe_allow_html=True)
            ec = st.text_input("ec", placeholder="e.g. EMP001",
                               key="ec", label_visibility="collapsed")
            st.markdown("<div class='lg-lbl'>🔒  Password</div>", unsafe_allow_html=True)
            ep = st.text_input("ep", type="password", placeholder="Password",
                               key="ep", label_visibility="collapsed")
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            if st.button("Sign in →", type="primary", use_container_width=True):
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
                            page="Home")
                        st.rerun()
                    else:
                        st.error(f"❌ Incorrect credentials.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ====================== APP SHELL ======================
role     = st.session_state.role
emp_code = st.session_state.emp_code
emp_name = st.session_state.emp_name
page     = st.session_state.page

render_header(emp_name, role)
st.markdown("<div class='page-content'>", unsafe_allow_html=True)

# ====================== ADMIN ======================
if role == "admin":
    bottom_nav_admin(page)

    today_plans = int((st.session_state.planned_df["VisitDate"]==date.today()).sum()) \
        if "VisitDate" in st.session_state.planned_df.columns else 0

    # ── HOME ──────────────────────────────────────────────
    if page == "Home":
        st.markdown(f"""
        <div class="greeting">
            <div class="greeting-hi">Admin Dashboard 📊</div>
            <div class="greeting-sub">Full overview of field activity</div>
            <div class="greeting-date">{date.today().strftime('%A, %d %B %Y')}</div>
        </div>""", unsafe_allow_html=True)

        stat_cards_2col([
            ("linear-gradient(90deg,#4f46e5,#7c3aed)","👥",
             len(st.session_state.employee_df),"Employees","Active team","#4f46e5"),
            ("linear-gradient(90deg,#06b6d4,#0284c7)","🏪",
             len(st.session_state.gst_df),"Stores","Total stores","#0891b2"),
            ("linear-gradient(90deg,#f59e0b,#d97706)","📋",
             len(st.session_state.planned_df),"All Plans","Total visits","#d97706"),
            ("linear-gradient(90deg,#10b981,#059669)","📍",
             today_plans,"Today","Visits today","#059669"),
        ])

        st.markdown("<div class='sec-hd'>📋 Recent Plans</div>", unsafe_allow_html=True)
        if not st.session_state.planned_df.empty:
            df_show = st.session_state.planned_df
            if "VisitDate" in df_show.columns:
                df_show = df_show.sort_values("VisitDate", ascending=False)
            st.dataframe(df_show.head(10), use_container_width=True, hide_index=True)
        else:
            empty_state("📋","No plans yet","Plans appear here once employees start planning.")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("🚪  Sign Out", use_container_width=True):
            for k,v in DEFAULTS.items(): st.session_state[k] = v
            st.rerun()

    # ── EMPLOYEES ─────────────────────────────────────────
    elif page == "Employees":
        st.markdown("<div class='page-title'>👥 Employees</div>", unsafe_allow_html=True)
        st.markdown("<div class='page-sub'>Manage your field team members</div>", unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["View","Add","Remove"])

        with tab1:
            disp = st.session_state.employee_df.drop(columns=["Password"], errors="ignore")
            if not disp.empty:
                st.markdown(f"<p style='font-size:13px;color:#9ca3af;margin-bottom:8px;'>{len(disp)} employees</p>", unsafe_allow_html=True)
                st.dataframe(disp, use_container_width=True, hide_index=True)
            else:
                empty_state("👥","No employees yet","Add your first team member.")

        with tab2:
            info_box("Employee code must be unique. They'll use it to log in.")
            with st.form("add_emp", clear_on_submit=True):
                ecode = st.text_input("Employee Code *", placeholder="e.g. EMP042")
                ename = st.text_input("Full Name *",     placeholder="e.g. Ramesh Kumar")
                epwd  = st.text_input("Password *", type="password", placeholder="Set a password")
                if st.form_submit_button("➕  Add Employee", type="primary", use_container_width=True):
                    if not ecode or not ename or not epwd:
                        st.error("All three fields are required.")
                    elif safe_col(st.session_state.employee_df,"EmployeeCode").astype(str).str.upper().eq(ecode.strip().upper()).any():
                        st.error(f"Code '{ecode.upper()}' already exists.")
                    else:
                        nr = pd.DataFrame([{"EmployeeCode":ecode.strip().upper(),"EmployeeName":ename.strip().title(),"Password":epwd.strip()}])
                        st.session_state.employee_df = pd.concat([st.session_state.employee_df,nr],ignore_index=True)
                        if save_to_supabase("employee_master", st.session_state.employee_df):
                            st.success(f"✅ {ename.strip().title()} added!"); st.rerun()

        with tab3:
            if st.session_state.employee_df.empty:
                empty_state("👥","No employees to remove","")
            else:
                warn_box("Removing an employee is permanent.")
                emp_del = st.selectbox("Select employee",
                    safe_col(st.session_state.employee_df,"EmployeeCode").unique())
                row = st.session_state.employee_df[safe_col(st.session_state.employee_df,"EmployeeCode")==emp_del]
                nm  = safe_col(row,"EmployeeName").iloc[0] if not row.empty else emp_del
                st.markdown(f"""
                <div class="store-item">
                    <div class="store-av av-r">👤</div>
                    <div>
                        <div class="s-nm">{nm}</div>
                        <div class="s-mt">{emp_del}</div>
                    </div>
                </div>""", unsafe_allow_html=True)
                if st.button("🗑  Confirm Remove", type="primary", use_container_width=True):
                    st.session_state.employee_df = st.session_state.employee_df[
                        safe_col(st.session_state.employee_df,"EmployeeCode")!=emp_del]
                    if save_to_supabase("employee_master", st.session_state.employee_df):
                        st.success(f"✅ {nm} removed."); st.rerun()

    # ── STORES ────────────────────────────────────────────
    elif page == "Stores":
        st.markdown("<div class='page-title'>🏪 Stores</div>", unsafe_allow_html=True)
        st.markdown("<div class='page-sub'>Manage your store master list</div>", unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["View","Add","Remove"])

        with tab1:
            if not st.session_state.gst_df.empty:
                cities = ["All"] + sorted(safe_col(st.session_state.gst_df,"City").dropna().unique().tolist())
                cf = st.selectbox("Filter by city", cities)
                df_s = st.session_state.gst_df if cf=="All" else \
                    st.session_state.gst_df[safe_col(st.session_state.gst_df,"City")==cf]
                st.markdown(f"<p style='font-size:13px;color:#9ca3af;margin-bottom:8px;'>{len(df_s)} stores</p>", unsafe_allow_html=True)
                st.dataframe(df_s, use_container_width=True, hide_index=True)
            else:
                empty_state("🏪","No stores yet","Add stores using the Add tab.")

        with tab2:
            info_box("GST number format: <b>22AAAAA0000A1Z5</b> (15 chars)")
            with st.form("add_store", clear_on_submit=True):
                sname   = st.text_input("Store Name *",  placeholder="e.g. Reliance Fresh")
                gstno   = st.text_input("GST Number *",  max_chars=15, placeholder="22AAAAA0000A1Z5")
                city    = st.text_input("City *",        placeholder="e.g. Lucknow")
                eopts   = safe_col(st.session_state.employee_df,"EmployeeCode").unique().tolist() or ["—"]
                emp_sel = st.selectbox("Assign to Employee *", eopts)
                if st.form_submit_button("➕  Add Store", type="primary", use_container_width=True):
                    gc = gstno.strip().upper()
                    if not sname or not gc or not city:
                        st.error("All fields are required.")
                    elif not is_valid_gstin(gc):
                        st.error("Invalid GSTIN. Example: 22AAAAA0000A1Z5")
                    elif safe_col(st.session_state.gst_df,"GSTNumber").astype(str).str.upper().eq(gc).any():
                        st.error(f"GST '{gc}' already exists.")
                    else:
                        nid = f"S{len(st.session_state.gst_df)+1:05d}"
                        ns  = pd.DataFrame([{"StoreID":nid,"StoreName":sname.strip().title(),
                                             "GSTNumber":gc,"City":city.strip().title(),"EmployeeCode":emp_sel}])
                        st.session_state.gst_df = pd.concat([st.session_state.gst_df,ns],ignore_index=True)
                        if save_to_supabase("gst_master", st.session_state.gst_df):
                            st.success(f"✅ {sname.strip().title()} added!"); st.rerun()

        with tab3:
            if st.session_state.gst_df.empty:
                empty_state("🏪","No stores to remove","")
            else:
                warn_box("Removing a store is permanent.")
                sdel = st.selectbox("Select store", safe_col(st.session_state.gst_df,"StoreID").unique())
                row  = st.session_state.gst_df[safe_col(st.session_state.gst_df,"StoreID")==sdel]
                snm  = safe_col(row,"StoreName").iloc[0] if not row.empty else sdel
                st.markdown(f"""
                <div class="store-item">
                    <div class="store-av av-r">🏪</div>
                    <div>
                        <div class="s-nm">{snm}</div>
                        <div class="s-mt">{sdel}</div>
                    </div>
                </div>""", unsafe_allow_html=True)
                if st.button("🗑  Confirm Remove", type="primary", use_container_width=True):
                    st.session_state.gst_df = st.session_state.gst_df[
                        safe_col(st.session_state.gst_df,"StoreID")!=sdel]
                    if save_to_supabase("gst_master", st.session_state.gst_df):
                        st.success(f"✅ {snm} removed."); st.rerun()

    # ── VIEW PLANS ────────────────────────────────────────
    elif page == "View Plans":
        st.markdown("<div class='page-title'>📋 View Plans</div>", unsafe_allow_html=True)
        st.markdown("<div class='page-sub'>Browse all employee beat plans</div>", unsafe_allow_html=True)

        with st.expander("🔍 Filter", expanded=False):
            femp  = st.selectbox("Employee",["All"]+list(safe_col(st.session_state.planned_df,"EmployeeName").dropna().unique()))
            fcity = st.selectbox("City",    ["All"]+list(safe_col(st.session_state.planned_df,"City").dropna().unique()))
            drange= st.date_input("Date Range", value=(date.today()-timedelta(days=30), date.today()))

        fp = st.session_state.planned_df.copy()
        if femp !="All" and "EmployeeName" in fp.columns: fp=fp[fp["EmployeeName"]==femp]
        if fcity!="All" and "City"         in fp.columns: fp=fp[fp["City"]==fcity]
        if isinstance(drange,(list,tuple)) and len(drange)==2 and "VisitDate" in fp.columns:
            fp=fp[(fp["VisitDate"]>=drange[0])&(fp["VisitDate"]<=drange[1])]

        stat_cards_2col([
            ("linear-gradient(90deg,#4f46e5,#7c3aed)","📋",len(fp),"Plans Found","Filtered","#4f46e5"),
            ("linear-gradient(90deg,#10b981,#059669)","🌍",safe_col(fp,"City").nunique(),"Cities","Covered","#059669"),
        ])

        if not fp.empty:
            st.dataframe(fp.sort_values("VisitDate",ascending=False) if "VisitDate" in fp.columns else fp,
                         use_container_width=True, hide_index=True)
            download_btn(fp,"admin_dl","Beat_Plan_Admin")
        else:
            empty_state("📋","No matching plans","Try adjusting your filters.")

    # ── REFRESH ───────────────────────────────────────────
    elif page == "Refresh":
        st.markdown("<div class='page-title'>🔄 Sync Data</div>", unsafe_allow_html=True)
        st.markdown("<div class='page-sub'>Pull latest records from Supabase</div>", unsafe_allow_html=True)
        info_box("Refreshes all tables: Employees, Stores, Plans and Admin.")
        if st.button("🔄  Refresh Now", type="primary", use_container_width=True):
            with st.spinner("Syncing…"):
                st.session_state.employee_df = load_from_supabase("employee_master", EMP_COLS)
                st.session_state.gst_df      = load_from_supabase("gst_master",      GST_COLS)
                st.session_state.planned_df  = load_from_supabase("planned_visits",  PLAN_COLS)
                st.session_state.admin_df    = load_from_supabase("admin_master",    ADMIN_COLS)
            st.success("✅ All data refreshed!"); st.rerun()

# ====================== EMPLOYEE ======================
else:
    bottom_nav_employee(page)

    my_stores = st.session_state.gst_df[
        safe_col(st.session_state.gst_df,"EmployeeCode").astype(str)==str(emp_code)
    ] if not st.session_state.gst_df.empty else pd.DataFrame(columns=GST_COLS)

    my_plans = st.session_state.planned_df[
        safe_col(st.session_state.planned_df,"EmployeeCode").astype(str)==str(emp_code)
    ]

    # ── HOME ──────────────────────────────────────────────
    if page == "Home":
        hr    = int(date.today().strftime("%d"))  # use day to avoid import datetime
        import datetime as dt_mod
        hour  = dt_mod.datetime.now().hour
        greet = "Good morning" if hour<12 else "Good afternoon" if hour<17 else "Good evening"
        first = emp_name.split()[0]

        st.markdown(f"""
        <div class="greeting">
            <div class="greeting-hi">{greet}, {first}! 👋</div>
            <div class="greeting-sub">Ready to plan your visits?</div>
            <div class="greeting-date">{date.today().strftime('%A, %d %B %Y')}</div>
        </div>""", unsafe_allow_html=True)

        today_p = my_plans[my_plans["VisitDate"]==date.today()] if "VisitDate" in my_plans.columns else pd.DataFrame()
        this_m  = my_plans[pd.to_datetime(safe_col(my_plans,"VisitDate"),errors="coerce").dt.month==date.today().month] \
            if "VisitDate" in my_plans.columns else pd.DataFrame()

        stat_cards_2col([
            ("linear-gradient(90deg,#4f46e5,#7c3aed)","🏪",
             len(my_stores),"My Stores",f"{safe_col(my_stores,'City').nunique()} cities","#4f46e5"),
            ("linear-gradient(90deg,#10b981,#059669)","📍",
             len(today_p),"Today",f"Max 10/day","#059669"),
            ("linear-gradient(90deg,#f59e0b,#d97706)","📅",
             len(this_m),"This Month",date.today().strftime("%b %Y"),"#d97706"),
            ("linear-gradient(90deg,#06b6d4,#0284c7)","📋",
             len(my_plans),"All Plans","All time","#0891b2"),
        ])

        # Quick Actions
        st.markdown("<div class='sec-hd'>Quick Actions</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class="qa-grid">
            <div class="qa-card">
                <div class="qa-icon" style="background:#eef2ff;">🎯</div>
                <div class="qa-label">New Beat Plan</div>
                <div class="qa-desc">Plan today's visits</div>
            </div>
            <div class="qa-card">
                <div class="qa-icon" style="background:#f0fdf4;">➕</div>
                <div class="qa-label">Add Store</div>
                <div class="qa-desc">Request new store</div>
            </div>
        </div>""", unsafe_allow_html=True)

        qa1, qa2 = st.columns(2)
        with qa1:
            if st.button("🎯  New Beat Plan", use_container_width=True): go("Beat Plan")
        with qa2:
            if st.button("➕  Add Store", use_container_width=True): go("Add Store")

        # Today's planned stores
        st.markdown("<div class='sec-hd'>📍 Today's Plan</div>", unsafe_allow_html=True)
        pc    = len(today_p)
        color = prog_color(pc)
        pct   = min(pc*10,100)

        st.markdown(f"""
        <div class="card">
            <div class="prog-row">
                <span class="prog-lbl">Progress</span>
                <span class="prog-num" style="color:{color};">{pc}/10</span>
            </div>
            <div class="prog-track">
                <div class="prog-fill" style="width:{pct}%;background:{color};"></div>
            </div>
            <div class="prog-hint">
                {"🚫 Daily limit reached" if pc>=10 else f"✅ {10-pc} more store(s) available"}
            </div>
        </div>""", unsafe_allow_html=True)

        if not today_p.empty:
            for _, row in today_p.iterrows():
                st.markdown(f"""
                <div class="store-item">
                    <div class="store-av av-g">✓</div>
                    <div style="flex:1;min-width:0;">
                        <div class="s-nm">{row.get('Store','—')}</div>
                        <div class="s-mt">{row.get('City','—')}</div>
                    </div>
                    <span class="bdg bdg-g">Planned</span>
                </div>""", unsafe_allow_html=True)
        else:
            empty_state("📍","Nothing planned today","Tap New Beat Plan to get started.")

        # Upcoming (top 3)
        if "VisitDate" in st.session_state.planned_df.columns:
            upcoming = st.session_state.planned_df[
                (safe_col(st.session_state.planned_df,"EmployeeCode").astype(str)==str(emp_code)) &
                (st.session_state.planned_df["VisitDate"] > date.today())
            ].sort_values("VisitDate")
            if not upcoming.empty:
                st.markdown("<div class='sec-hd'>📆 Coming Up</div>", unsafe_allow_html=True)
                for vd in sorted(upcoming["VisitDate"].unique())[:3]:
                    pl     = upcoming[upcoming["VisitDate"]==vd]
                    cities = ", ".join(sorted(safe_col(pl,"City").dropna().unique().tolist()))
                    stores = safe_col(pl,"Store").dropna().unique().tolist()
                    pills  = "".join(f"<span class='tl-pill'>{s}</span>" for s in stores[:3])
                    if len(stores)>3: pills += f"<span class='tl-pill'>+{len(stores)-3}</span>"
                    st.markdown(f"""
                    <div class="tl-item">
                        <div class="tl-date fut">
                            <div class="tl-day">{vd.strftime('%d')}</div>
                            <div class="tl-mon">{vd.strftime('%b')}</div>
                        </div>
                        <div>
                            <div class="tl-title">{len(pl)} stores · {vd.strftime('%a')}</div>
                            <div class="tl-sub">{cities}</div>
                            <div class="tl-pills">{pills}</div>
                        </div>
                    </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        if st.button("🚪  Sign Out", use_container_width=True):
            for k,v in DEFAULTS.items(): st.session_state[k] = v
            st.rerun()

    # ── BEAT PLAN ─────────────────────────────────────────
    elif page == "Beat Plan":
        st.markdown("<div class='page-title'>🎯 Beat Plan</div>", unsafe_allow_html=True)
        st.markdown("<div class='page-sub'>Add stores to your visit list</div>", unsafe_allow_html=True)

        if my_stores.empty:
            empty_state("⚠️","No stores assigned","Contact your admin to assign stores.")
            st.stop()

        visit_date = st.date_input("📅 Visit Date", value=date.today(), key="bd",
                                   min_value=date.today()-timedelta(days=7))

        city_opts  = sorted(safe_col(my_stores,"City").dropna().unique().tolist())
        sel_cities = st.multiselect(f"🌍 Filter Cities (max 3)", city_opts,
                                    max_selections=3, key="cms")
        if st.button("🔍  Apply", use_container_width=True):
            st.session_state.selected_cities = sel_cities; st.rerun()

        daily = my_plans[my_plans["VisitDate"]==visit_date] if "VisitDate" in my_plans.columns else pd.DataFrame(columns=PLAN_COLS)
        pc    = len(daily)
        color = prog_color(pc)
        pct   = min(pc*10,100)

        st.markdown(f"""
        <div class="card">
            <div class="card-hdr">
                <div class="card-hdr-icon" style="background:#eef2ff;">📊</div>
                {visit_date.strftime('%d %b %Y')}
                <span class="card-pill"
                    style="background:{'#fef2f2' if pc>=10 else '#eef2ff'};
                           color:{'#b91c1c' if pc>=10 else '#4338ca'};">{pc}/10</span>
            </div>
            <div class="prog-row">
                <span class="prog-lbl">
                    {"🚫 Limit reached" if pc>=10 else f"✅ {10-pc} more available"}
                </span>
                <span class="prog-num" style="color:{color};">{pct}%</span>
            </div>
            <div class="prog-track">
                <div class="prog-fill" style="width:{pct}%;background:{color};"></div>
            </div>
        </div>""", unsafe_allow_html=True)

        if not daily.empty:
            with st.expander(f"✅ Planned ({pc} stores)"):
                cols = [c for c in ["Store","City","GSTNumber"] if c in daily.columns]
                st.dataframe(daily[cols], use_container_width=True, hide_index=True)

        if pc < 10:
            show_cities = st.session_state.selected_cities or safe_col(my_stores,"City").unique().tolist()
            avail = my_stores[
                safe_col(my_stores,"City").isin(show_cities) &
                ~safe_col(my_stores,"StoreID").isin(safe_col(daily,"StoreID").tolist())
            ]

            st.markdown(
                f"<div class='sec-hd'>🏪 Available <span class='sec-ct'>{len(avail)}</span></div>",
                unsafe_allow_html=True)

            if avail.empty:
                empty_state("🎉","All done!","All stores planned for selected cities.")
            else:
                for idx, row in avail.iterrows():
                    c1, c2 = st.columns([4,1])
                    with c1:
                        st.markdown(f"""
                        <div class="store-item">
                            <div class="store-av av-i">🏪</div>
                            <div style="flex:1;min-width:0;">
                                <div class="s-nm">{row.get('StoreName','—')}</div>
                                <div class="s-mt">{row.get('City','—')} · {row.get('GSTNumber','—')}</div>
                            </div>
                        </div>""", unsafe_allow_html=True)
                    with c2:
                        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
                        if st.button("➕", key=f"add_{idx}_{visit_date}", use_container_width=True):
                            nr = pd.DataFrame([{
                                "EmployeeCode":emp_code,"EmployeeName":emp_name,
                                "City":row.get("City",""),"Store":row.get("StoreName",""),
                                "StoreID":row.get("StoreID",""),"GSTNumber":row.get("GSTNumber",""),
                                "VisitDate":visit_date
                            }])
                            st.session_state.planned_df = pd.concat([st.session_state.planned_df,nr],ignore_index=True)
                            if save_to_supabase("planned_visits", st.session_state.planned_df):
                                st.success(f"✅ {row.get('StoreName','')} added!"); st.rerun()

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        download_btn(my_plans,"emp_dl",f"Beat_Plan_{emp_code}")

    # ── MY PLANS ──────────────────────────────────────────
    elif page == "My Plans":
        st.markdown("<div class='page-title'>📅 My Plans</div>", unsafe_allow_html=True)
        st.markdown("<div class='page-sub'>All your scheduled store visits</div>", unsafe_allow_html=True)

        if my_plans.empty:
            empty_state("📅","No plans yet","Go to Beat Plan to schedule visits.")
        else:
            this_m = my_plans[pd.to_datetime(safe_col(my_plans,"VisitDate"),errors="coerce").dt.month==date.today().month] \
                if "VisitDate" in my_plans.columns else pd.DataFrame()
            stat_cards_2col([
                ("linear-gradient(90deg,#4f46e5,#7c3aed)","📋",len(my_plans),"Total Plans","All time","#4f46e5"),
                ("linear-gradient(90deg,#10b981,#059669)","📅",len(this_m),"This Month",date.today().strftime("%b"),"#059669"),
                ("linear-gradient(90deg,#06b6d4,#0284c7)","🌍",safe_col(my_plans,"City").nunique(),"Cities","Covered","#0891b2"),
                ("linear-gradient(90deg,#f59e0b,#d97706)","🏪",safe_col(my_plans,"Store").nunique(),"Stores","Unique","#d97706"),
            ])

            with st.expander("🔍 Filter", expanded=False):
                fc = st.selectbox("City",["All"]+sorted(safe_col(my_plans,"City").dropna().unique().tolist()))
                fd = st.date_input("From date", value=date.today()-timedelta(days=30), key="mpd")

            df_mp = my_plans.copy()
            if fc!="All" and "City" in df_mp.columns: df_mp=df_mp[df_mp["City"]==fc]
            if "VisitDate" in df_mp.columns: df_mp=df_mp[df_mp["VisitDate"]>=fd]

            st.dataframe(
                df_mp.sort_values("VisitDate",ascending=False) if "VisitDate" in df_mp.columns else df_mp,
                use_container_width=True, hide_index=True)
            download_btn(df_mp,"my_dl",f"My_Plans_{emp_code}")

    # ── UPCOMING ──────────────────────────────────────────
    elif page == "Upcoming":
        st.markdown("<div class='page-title'>📆 Upcoming</div>", unsafe_allow_html=True)
        st.markdown("<div class='page-sub'>Your planned visits from today onwards</div>", unsafe_allow_html=True)

        if "VisitDate" not in st.session_state.planned_df.columns:
            empty_state("📆","No upcoming visits","Plan visits in Beat Plan.")
        else:
            upcoming = st.session_state.planned_df[
                (safe_col(st.session_state.planned_df,"EmployeeCode").astype(str)==str(emp_code)) &
                (st.session_state.planned_df["VisitDate"] >= date.today())
            ].sort_values("VisitDate")

            if upcoming.empty:
                empty_state("📆","No upcoming visits","Plan visits in Beat Plan.")
            else:
                total_days   = len(upcoming["VisitDate"].unique())
                total_stores = len(upcoming)
                st.markdown(f"""
                <div class="info-box">
                    📅  <b>{total_stores} visits</b> across <b>{total_days} days</b>
                </div>""", unsafe_allow_html=True)

                for vd in sorted(upcoming["VisitDate"].unique()):
                    pl     = upcoming[upcoming["VisitDate"]==vd]
                    bc     = "tod" if vd==date.today() else "fut"
                    cities = ", ".join(sorted(safe_col(pl,"City").dropna().unique().tolist()))
                    stores = safe_col(pl,"Store").dropna().unique().tolist()
                    pills  = "".join(f"<span class='tl-pill'>{s}</span>" for s in stores[:4])
                    if len(stores)>4: pills += f"<span class='tl-pill'>+{len(stores)-4}</span>"
                    today_tag = "<span class='bdg bdg-p'>Today</span>" if vd==date.today() else ""
                    st.markdown(f"""
                    <div class="tl-item">
                        <div class="tl-date {bc}">
                            <div class="tl-day">{vd.strftime('%d')}</div>
                            <div class="tl-mon">{vd.strftime('%b')}</div>
                        </div>
                        <div style="flex:1;min-width:0;">
                            <div class="tl-title">{len(pl)} stores · {vd.strftime('%A')}</div>
                            <div class="tl-sub">{cities}</div>
                            <div class="tl-pills">{pills}</div>
                        </div>
                        {today_tag}
                    </div>""", unsafe_allow_html=True)

    # ── ANALYTICS ─────────────────────────────────────────
    elif page == "Analytics":
        st.markdown("<div class='page-title'>📈 Analytics</div>", unsafe_allow_html=True)
        st.markdown("<div class='page-sub'>Your personal performance insights</div>", unsafe_allow_html=True)

        if my_plans.empty:
            empty_state("📈","No data yet","Your analytics appear once you plan visits.")
        else:
            this_m = my_plans[pd.to_datetime(safe_col(my_plans,"VisitDate"),errors="coerce").dt.month==date.today().month] \
                if "VisitDate" in my_plans.columns else pd.DataFrame()
            stat_cards_2col([
                ("linear-gradient(90deg,#4f46e5,#7c3aed)","📋",len(my_plans),"Total Visits","All time","#4f46e5"),
                ("linear-gradient(90deg,#10b981,#059669)","📅",len(this_m),"This Month",date.today().strftime("%b"),"#059669"),
                ("linear-gradient(90deg,#06b6d4,#0284c7)","🌍",safe_col(my_plans,"City").nunique(),"Cities","Covered","#0891b2"),
                ("linear-gradient(90deg,#f59e0b,#d97706)","🏪",safe_col(my_plans,"Store").nunique(),"Stores","Unique","#d97706"),
            ])

            st.markdown("<div class='sec-hd'>Visits by City</div>", unsafe_allow_html=True)
            if "City" in my_plans.columns:
                st.bar_chart(my_plans.groupby("City").size(), color="#4f46e5")

            st.markdown("<div class='sec-hd'>Monthly Trend</div>", unsafe_allow_html=True)
            if "VisitDate" in my_plans.columns:
                tmp = my_plans.copy()
                tmp["Month"] = pd.to_datetime(tmp["VisitDate"],errors="coerce").dt.to_period("M").astype(str)
                st.line_chart(tmp.groupby("Month").size(), color="#06b6d4")

            st.markdown("<div class='sec-hd'>Top Stores <span class='sec-ct'>Top 10</span></div>", unsafe_allow_html=True)
            if "Store" in my_plans.columns:
                top = my_plans.groupby("Store").agg(
                    Visits=("Store","count"), City=("City","first")
                ).reset_index().sort_values("Visits",ascending=False).head(10)
                st.dataframe(top, use_container_width=True, hide_index=True)

    # ── ADD STORE ─────────────────────────────────────────
    elif page == "Add Store":
        st.markdown("<div class='page-title'>➕ Add Store</div>", unsafe_allow_html=True)
        st.markdown("<div class='page-sub'>Request a store for your territory</div>", unsafe_allow_html=True)

        info_box("GSTIN format: <b>22AAAAA0000A1Z5</b> (15 characters)")

        with st.form("store_req", clear_on_submit=True):
            sname = st.text_input("Store Name *",  placeholder="e.g. Reliance Fresh")
            city  = st.text_input("City *",        placeholder="e.g. Lucknow")
            gst   = st.text_input("GST Number *",  max_chars=15, placeholder="22AAAAA0000A1Z5")
            st.text_area("Remarks (optional)", height=80, placeholder="Notes for admin…")
            if st.form_submit_button("➕  Add to My Territory", type="primary", use_container_width=True):
                gc = gst.strip().upper()
                if not sname or not city or not gc:
                    st.error("All fields are required.")
                elif not is_valid_gstin(gc):
                    st.error("Invalid GSTIN. Format: 22AAAAA0000A1Z5")
                elif safe_col(st.session_state.gst_df,"GSTNumber").astype(str).str.upper().eq(gc).any():
                    st.error(f"GSTIN '{gc}' already exists.")
                else:
                    nid = f"S{len(st.session_state.gst_df)+1:05d}"
                    ns  = pd.DataFrame([{"StoreID":nid,"StoreName":sname.strip().title(),
                                         "GSTNumber":gc,"City":city.strip().title(),"EmployeeCode":emp_code}])
                    st.session_state.gst_df = pd.concat([st.session_state.gst_df,ns],ignore_index=True)
                    if save_to_supabase("gst_master", st.session_state.gst_df):
                        st.success(f"✅ {sname.strip().title()} added to {city.strip().title()}!"); st.rerun()

st.markdown("</div>", unsafe_allow_html=True)  # close page-content

# ====================== FOOTER ======================
st.markdown("""
<div style='text-align:center;font-size:12px;color:#c4c9d9;padding:16px 0 90px;'>
    Beat Plan Pro · 2026 · Built by Bipin Pandey
</div>""", unsafe_allow_html=True)
