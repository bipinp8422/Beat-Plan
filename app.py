import streamlit as st
import pandas as pd
from datetime import date, timedelta
import calendar
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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: #f0f4f8; }

    .main-header {
        font-size: 42px; font-weight: 900; letter-spacing: -1.5px;
        background: linear-gradient(135deg, #1a56db 0%, #06b6d4 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin: 10px 0 4px;
    }
    .sub-header {
        text-align: center; color: #64748b; font-size: 14px;
        font-weight: 600; margin-bottom: 28px; letter-spacing: 0.5px;
    }

    .metric-card {
        background: #ffffff; padding: 22px 20px; border-radius: 18px;
        border: 1.5px solid #e8edf5;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        margin-bottom: 16px; position: relative; overflow: hidden;
    }
    .metric-card::before {
        content: ''; position: absolute; top: 0; left: 0;
        width: 4px; height: 100%; border-radius: 18px 0 0 18px;
    }
    .metric-card.blue::before  { background: linear-gradient(180deg, #1a56db, #06b6d4); }
    .metric-card.green::before { background: linear-gradient(180deg, #10b981, #34d399); }
    .metric-card.amber::before { background: linear-gradient(180deg, #f59e0b, #fbbf24); }
    .metric-card.red::before   { background: linear-gradient(180deg, #ef4444, #f87171); }
    .metric-card.purple::before{ background: linear-gradient(180deg, #8b5cf6, #a78bfa); }

    .metric-icon  { font-size: 28px; margin-bottom: 10px; }
    .metric-label { color: #94a3b8; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 6px; }
    .metric-value { font-size: 34px; font-weight: 900; color: #0f172a; line-height: 1; }
    .metric-sub   { font-size: 12px; color: #94a3b8; margin-top: 6px; font-weight: 500; }

    .emp-card {
        background: #ffffff; border-radius: 14px; padding: 16px 18px;
        margin-bottom: 10px; border: 1.5px solid #e8edf5;
        box-shadow: 0 1px 6px rgba(0,0,0,0.05);
        display: flex; align-items: center; gap: 14px;
    }
    .emp-avatar {
        width: 44px; height: 44px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-weight: 800; font-size: 16px; flex-shrink: 0;
    }
    .emp-avatar.done    { background: #d1fae5; color: #065f46; }
    .emp-avatar.pending { background: #fee2e2; color: #991b1b; }
    .emp-info           { flex: 1; }
    .emp-name           { font-weight: 700; color: #1e293b; font-size: 15px; }
    .emp-code           { font-size: 12px; color: #94a3b8; font-weight: 500; margin-top: 2px; }
    .emp-badge {
        padding: 4px 12px; border-radius: 20px; font-size: 12px;
        font-weight: 700; flex-shrink: 0;
    }
    .badge-done    { background: #d1fae5; color: #065f46; }
    .badge-pending { background: #fee2e2; color: #991b1b; }
    .emp-count { font-size: 13px; color: #64748b; font-weight: 600; margin-top: 3px; }

    .role-chip {
        display: inline-block; padding: 2px 10px; border-radius: 20px;
        font-size: 11px; font-weight: 700; margin-left: 6px;
    }
    .role-chip.asm  { background: #ede9fe; color: #5b21b6; }
    .role-chip.emp  { background: #e0f2fe; color: #075985; }

    .section-head {
        font-size: 15px; font-weight: 800; color: #1e293b; margin: 20px 0 12px;
        display: flex; align-items: center; gap: 8px;
    }
    .section-line { flex: 1; height: 1px; background: #e2e8f0; }

    .store-card {
        background: #ffffff; padding: 16px 20px; border-radius: 14px;
        border: 1.5px solid #e8edf5; box-shadow: 0 1px 6px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    .store-name  { font-weight: 700; font-size: 16px; color: #1e293b; margin-bottom: 6px; }
    .store-meta  { font-size: 13px; color: #64748b; line-height: 1.8; }
    .store-chip  {
        display: inline-block; padding: 2px 10px; border-radius: 20px;
        background: #eff6ff; color: #1a56db; font-size: 12px; font-weight: 600;
        margin-right: 8px;
    }

    .progress-wrap {
        background: #ffffff; border-radius: 16px; padding: 20px 22px;
        border: 1.5px solid #e8edf5; box-shadow: 0 1px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .progress-label { font-weight: 700; color: #1e293b; font-size: 15px; }
    .progress-track { height: 10px; background: #f1f5f9; border-radius: 10px; margin: 10px 0 6px; overflow: hidden; }
    .progress-fill  { height: 100%; border-radius: 10px; transition: width .4s ease; }

    .info-banner {
        background: linear-gradient(135deg, #eff6ff, #e0f2fe);
        border: 1.5px solid #bfdbfe; border-radius: 12px;
        padding: 14px 18px; margin-bottom: 16px;
        font-size: 14px; color: #1e40af; font-weight: 600;
    }
    .warning-banner {
        background: linear-gradient(135deg, #fff7ed, #fef2f2);
        border: 1.5px solid #fed7aa; border-radius: 12px;
        padding: 14px 18px; margin-bottom: 16px;
        font-size: 14px; color: #9a3412; font-weight: 600;
    }

    .stButton > button {
        border-radius: 10px !important; height: 44px !important;
        font-weight: 700 !important; font-size: 14px !important;
        background: linear-gradient(135deg, #1a56db, #06b6d4) !important;
        color: white !important; border: none !important;
        box-shadow: 0 2px 8px rgba(26,86,219,0.3) !important;
        transition: transform .1s ease !important;
    }
    .stButton > button:hover { transform: translateY(-1px) !important; }
    .stButton > button[kind="secondary"] {
        background: #fff !important; color: #ef4444 !important;
        border: 1.5px solid #fecaca !important; box-shadow: none !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
    }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    [data-testid="stSidebar"] .stRadio label { font-weight: 600 !important; }

    .stTextInput > div > div > input {
        border-radius: 10px !important; border: 1.5px solid #e2e8f0 !important;
        font-size: 14px !important;
    }

    [data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

    .stTabs [data-baseweb="tab"] { font-weight: 600; }
    .stTabs [data-baseweb="tab-highlight"] { background: #1a56db; }

    .del-row {
        background: #fff5f5; border: 1.5px solid #fecaca;
        border-radius: 12px; padding: 14px 18px; margin-bottom: 8px;
        display: flex; align-items: center; gap: 12px;
    }
    .del-info { flex: 1; font-size: 14px; color: #1e293b; }
    .del-date { font-size: 12px; color: #94a3b8; margin-top: 3px; }

    .marquee-wrap {
        background: linear-gradient(135deg, #fff7ed, #fef2f2);
        border: 1.5px solid #fed7aa; border-radius: 12px;
        padding: 10px 0; margin-bottom: 18px; overflow: hidden;
        display: flex; align-items: center; white-space: nowrap;
    }
    .marquee-tag {
        flex-shrink: 0; background: #f59e0b; color: #fff; font-weight: 800;
        font-size: 12px; padding: 6px 14px; border-radius: 8px;
        margin: 0 12px; letter-spacing: 0.5px;
    }
    .marquee-track { flex: 1; overflow: hidden; position: relative; }
    .marquee-content {
        display: inline-block; white-space: nowrap;
        animation: marquee-scroll 140s linear infinite;
        font-size: 14px; font-weight: 600; color: #9a3412;
    }
    .marquee-content span { margin-right: 50px; }
    .marquee-wrap:hover .marquee-content { animation-play-state: paused; }
    @keyframes marquee-scroll {
        0%   { transform: translateX(0%); }
        100% { transform: translateX(-50%); }
    }
</style>
""", unsafe_allow_html=True)

# ====================== COLUMN NAME NORMALIZER ======================
COLUMN_MAP = {
    "EmployeeCode": ["employeecode", "employee_code"],
    "EmployeeName": ["employeename", "employee_name"],
    "Password":     ["password"],
    "Role":         ["role", "user_role", "userrole"],
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

# ====================== DATE HELPERS ======================
def get_next_month_range():
    """Returns (first_day, last_day) of next month."""
    today = date.today()
    if today.month == 12:
        nm_year, nm_month = today.year + 1, 1
    else:
        nm_year, nm_month = today.year, today.month + 1
    first_day = date(nm_year, nm_month, 1)
    last_day  = date(nm_year, nm_month, calendar.monthrange(nm_year, nm_month)[1])
    return first_day, last_day

def get_next_month_sundays():
    """Returns a sorted list of all Sunday dates in next month."""
    first_day, last_day = get_next_month_range()
    sundays = []
    d = first_day
    while d <= last_day:
        if d.weekday() == 6:  # Sunday
            sundays.append(d)
        d += timedelta(days=1)
    return sundays

def is_after_cutoff():
    """Returns True if today's date is > 23 of current month."""
    return date.today().day > 23

def is_employee_planning_allowed():
    """Employees can only plan for next month dates."""
    return True  # Always allowed, but dates are restricted to next month

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
    if "Role" in df.columns:
        df["Role"] = df["Role"].astype(str).str.strip()
        df.loc[~df["Role"].isin(["Employee", "ASM"]), "Role"] = "Employee"
    return df

def load_from_supabase(table_name, columns, keep_id=False):
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
            df = clean_dataframe(df, columns)
            if keep_id and "id" in df.columns:
                pass
            elif not keep_id and "id" in df.columns:
                df = df.drop(columns=["id"])
            return df
        return pd.DataFrame(columns=columns)
    except Exception as e:
        st.warning(f"⚠️ Error loading `{table_name}`: {e}")
        return pd.DataFrame(columns=columns)

def save_master_to_supabase(table_name, df):
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

def insert_planned_visit(record: dict):
    try:
        rec = {k: v for k, v in record.items() if k != "id"}
        if "VisitDate" in rec:
            v = rec["VisitDate"]
            if hasattr(v, "strftime"):
                rec["VisitDate"] = v.strftime("%Y-%m-%d")
            else:
                rec["VisitDate"] = str(v)
        response = supabase.table("planned_visits").insert(rec).execute()
        if response.data:
            return response.data[0].get("id")
        return None
    except Exception as e:
        st.error(f"❌ Insert failed: {e}")
        return None

def delete_planned_visit(row_id):
    try:
        supabase.table("planned_visits").delete().eq("id", int(row_id)).execute()
        return True
    except Exception as e:
        st.error(f"❌ Delete failed: {e}")
        return False

def insert_gst_row(record: dict):
    try:
        rec = {k: v for k, v in record.items() if k != "id"}
        response = supabase.table("gst_master").insert(rec).execute()
        if response.data:
            return response.data[0].get("id")
        return None
    except Exception as e:
        st.error(f"❌ Store insert failed: {e}")
        return None

def delete_gst_row(store_id):
    try:
        supabase.table("gst_master").delete().eq("StoreID", str(store_id)).execute()
        return True
    except Exception as e:
        st.error(f"❌ Store delete failed: {e}")
        return False

def insert_employee_row(record: dict):
    try:
        rec = {k: v for k, v in record.items() if k != "id"}
        response = supabase.table("employee_master").insert(rec).execute()
        if response.data:
            return response.data[0].get("id")
        return None
    except Exception as e:
        st.error(f"❌ Employee insert failed: {e}")
        return None

def delete_employee_row(emp_code):
    try:
        supabase.table("employee_master").delete().eq("EmployeeCode", str(emp_code)).execute()
        return True
    except Exception as e:
        st.error(f"❌ Employee delete failed: {e}")
        return False

# ====================== COLUMN CONSTANTS ======================
EMP_COLS   = ["EmployeeCode", "EmployeeName", "Password", "Role"]
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
    st.session_state.planned_df = load_from_supabase("planned_visits", PLAN_COLS, keep_id=True)
if "admin_df" not in st.session_state:
    st.session_state.admin_df = load_from_supabase("admin_master", ADMIN_COLS)

for k, v in {
    "logged_in": False, "role": "", "emp_code": "", "emp_name": "",
    "is_asm": False, "selected_cities": [], "auto_plan_done_month": None
}.items():
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

def gst_chip_html(row):
    """Returns a GST chip only if a GST number is actually present (ASM stores may have none)."""
    gst_val = str(row.get("GSTNumber", "") or "").strip()
    if gst_val and gst_val.lower() not in ("nan", "none"):
        return f"<span class='store-chip'>🧾 {gst_val}</span>"
    return ""

def get_employee_role(emp_code):
    """Returns 'ASM' or 'Employee' for a given employee code."""
    emp_df = st.session_state.employee_df
    if emp_df.empty or "EmployeeCode" not in emp_df.columns:
        return "Employee"
    match = emp_df[emp_df["EmployeeCode"].astype(str) == str(emp_code)]
    if match.empty:
        return "Employee"
    return str(match.iloc[0].get("Role", "Employee")).strip() or "Employee"

def get_pending_stores_for_employee(emp_code):
    gst_df = st.session_state.gst_df
    plan_df = st.session_state.planned_df

    emp_stores = gst_df[safe_col(gst_df, "EmployeeCode").astype(str) == str(emp_code)] \
        if not gst_df.empty else pd.DataFrame(columns=GST_COLS)

    if emp_stores.empty:
        return emp_stores

    ever_planned_ids = set(
        safe_col(
            plan_df[safe_col(plan_df, "EmployeeCode").astype(str) == str(emp_code)],
            "StoreID"
        ).astype(str).str.strip()
    ) if not plan_df.empty else set()

    pending = emp_stores[~safe_col(emp_stores, "StoreID").astype(str).str.strip().isin(ever_planned_ids)]
    return pending

def download_beat_plan_button(df, key, filename_prefix="Beat_Plan"):
    if not df.empty:
        dl_df = df.drop(columns=["id"], errors="ignore")
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            dl_df.to_excel(writer, index=False, sheet_name="Beat Plan")
        output.seek(0)
        st.download_button(
            label="📥 Download Beat Plan (Excel)",
            data=output.getvalue(),
            file_name=f"{filename_prefix}_{date.today().strftime('%Y-%m-%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key=key,
        )

def download_pending_button(pend_df, key, sel_date):
    if pend_df is None or pend_df.empty:
        return
    cols = [c for c in ["EmployeeCode", "EmployeeName"] if c in pend_df.columns]
    dl_df = pend_df[cols].copy() if cols else pend_df.copy()
    dl_df.insert(0, "Date", sel_date.strftime("%Y-%m-%d"))
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        dl_df.to_excel(writer, index=False, sheet_name="Pending")
    output.seek(0)
    st.download_button(
        label="📥 Download Pending List (Excel)",
        data=output.getvalue(),
        file_name=f"Pending_Beat_Plan_{sel_date.strftime('%Y-%m-%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        key=key,
    )

def download_pending_stores_button(pend_df, key, filename_prefix="Pending_Stores"):
    if pend_df is None or pend_df.empty:
        return
    cols = [c for c in ["EmployeeCode", "EmployeeName", "StoreID", "StoreName", "City", "GSTNumber"] if c in pend_df.columns]
    dl_df = pend_df[cols].copy() if cols else pend_df.copy()
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        dl_df.to_excel(writer, index=False, sheet_name="Pending Stores")
    output.seek(0)
    st.download_button(
        label="📥 Download Pending Stores (Excel)",
        data=output.getvalue(),
        file_name=f"{filename_prefix}_{date.today().strftime('%Y-%m-%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        key=key,
    )

def render_pending_marquee(pend_stores):
    if pend_stores is None or pend_stores.empty:
        return
    names = []
    for _, r in pend_stores.iterrows():
        nm = r.get("StoreName", "—")
        ct = r.get("City", "")
        names.append(f"🏪 {nm} ({ct})" if ct else f"🏪 {nm}")
    content = "".join([f"<span>{n}</span>" for n in names * 2])
    st.markdown(f"""
        <div class='marquee-wrap'>
            <div class='marquee-tag'>📦 {len(pend_stores)} NEVER PLANNED</div>
            <div class='marquee-track'>
                <div class='marquee-content'>{content}</div>
            </div>
        </div>""", unsafe_allow_html=True)

def section_header(icon, title):
    st.markdown(f"""
        <div class='section-head'>
            {icon} {title}
            <div class='section-line'></div>
        </div>""", unsafe_allow_html=True)

def fetch_beat_status_live(sel_date):
    try:
        date_str = sel_date.strftime("%Y-%m-%d")
        all_rows = []
        batch_size = 1000
        offset = 0
        while True:
            resp = (
                supabase
                .table("planned_visits")
                .select("*")
                .range(offset, offset + batch_size - 1)
                .execute()
            )
            if not resp.data:
                break
            all_rows.extend(resp.data)
            if len(resp.data) < batch_size:
                break
            offset += batch_size

        if not all_rows:
            return {}

        df = pd.DataFrame(all_rows)
        df = normalize_columns(df)

        if "VisitDate" not in df.columns:
            st.warning("⚠️ VisitDate column not found in planned_visits table.")
            return {}

        df["VisitDate"] = pd.to_datetime(df["VisitDate"], errors="coerce").dt.strftime("%Y-%m-%d")
        df_date = df[df["VisitDate"] == date_str]

        result = {}
        if "EmployeeCode" in df_date.columns:
            for ec in df_date["EmployeeCode"].astype(str):
                ec = ec.strip()
                if ec and ec.lower() != "nan":
                    result[ec] = result.get(ec, 0) + 1
        return result

    except Exception as e:
        st.warning(f"⚠️ Live DB check failed: {e}")
        return {}


def fetch_emp_plans_live(emp_code, sel_date):
    try:
        date_str = sel_date.strftime("%Y-%m-%d")
        all_rows = []
        batch_size = 1000
        offset = 0
        while True:
            resp = (
                supabase
                .table("planned_visits")
                .select("*")
                .range(offset, offset + batch_size - 1)
                .execute()
            )
            if not resp.data:
                break
            all_rows.extend(resp.data)
            if len(resp.data) < batch_size:
                break
            offset += batch_size

        if not all_rows:
            return pd.DataFrame()

        df = pd.DataFrame(all_rows)
        df = normalize_columns(df)

        if "VisitDate" in df.columns:
            df["VisitDate"] = pd.to_datetime(df["VisitDate"], errors="coerce").dt.strftime("%Y-%m-%d")
            df = df[df["VisitDate"] == date_str]
        if "EmployeeCode" in df.columns:
            df = df[df["EmployeeCode"].astype(str).str.strip() == str(emp_code).strip()]

        return df.reset_index(drop=True)

    except Exception as e:
        st.warning(f"⚠️ Could not load details: {e}")
        return pd.DataFrame()

# ====================== BEAT PLAN PIVOT BUILDER ======================
def build_beat_plan_pivot(fp_df):
    pivot_index = [c for c in ["EmployeeCode", "EmployeeName", "GSTNumber", "Store", "City", "StoreID"] if c in fp_df.columns]
    if not pivot_index or "VisitDate" not in fp_df.columns:
        return pd.DataFrame()

    pv = fp_df.copy()
    pv["VisitDate"] = pd.to_datetime(pv["VisitDate"], errors="coerce")
    pv = pv.dropna(subset=["VisitDate"])
    if pv.empty:
        return pd.DataFrame()

    pivot = pv.pivot_table(
        index=pivot_index,
        columns="VisitDate",
        values="VisitDate",
        aggfunc="count",
        fill_value=0,
    )
    pivot = pivot.reindex(sorted(pivot.columns), axis=1)
    pivot.columns = [c.strftime("%Y-%m-%d") for c in pivot.columns]
    pivot["Grand Total"] = pivot.sum(axis=1)
    pivot = pivot.reset_index()
    ordered_front = [c for c in ["EmployeeCode", "EmployeeName", "GSTNumber", "Store", "City", "StoreID"] if c in pivot.columns]
    other_cols = [c for c in pivot.columns if c not in ordered_front]
    pivot = pivot[ordered_front + other_cols]
    return pivot

# ====================== AUTO-PLAN PENDING STORES (AFTER 23rd) ======================
def auto_plan_pending_stores_all_employees(dry_run=False):
    """
    For every employee (and ASM), find all never-planned stores and auto-schedule them
    starting on the FIRST Sunday of next month (the planning month).
    Round-robins across all Sundays so nothing is skipped.
    Returns a summary dict: {emp_code: {"planned": [...], "skipped": [...]}}
    """
    emp_df  = st.session_state.employee_df
    sundays = get_next_month_sundays()   # sorted list, earliest first

    if not sundays:
        return {"error": "No Sundays found in next month."}

    if emp_df.empty or "EmployeeCode" not in emp_df.columns:
        return {"error": "No employees found."}

    plan_df = st.session_state.planned_df.copy()

    summary     = {}
    new_records = []

    for _, erow in emp_df.iterrows():
        ec = str(erow.get("EmployeeCode", "")).strip()
        en = erow.get("EmployeeName", ec)
        if not ec or ec.lower() == "nan":
            continue

        pending = get_pending_stores_for_employee(ec)
        if pending.empty:
            summary[ec] = {"name": en, "planned": [], "skipped": []}
            continue

        emp_planned = []
        emp_skipped = []

        # Round-robin across all Sundays — NO hard cap per Sunday.
        # store[0] → Sunday[0], store[1] → Sunday[1], ... wraps back to Sunday[0].
        # This guarantees every pending store gets a date; nothing is skipped.
        sunday_list = sundays  # sorted earliest → latest
        n_sundays   = len(sunday_list)

        for store_idx, (_, store_row) in enumerate(pending.iterrows()):
            target_sunday = sunday_list[store_idx % n_sundays]

            new_record = {
                "EmployeeCode": ec,
                "EmployeeName": en,
                "City":         store_row.get("City", ""),
                "Store":        store_row.get("StoreName", ""),
                "StoreID":      store_row.get("StoreID", ""),
                "GSTNumber":    store_row.get("GSTNumber", ""),
                "VisitDate":    target_sunday,
            }

            if not dry_run:
                new_id = insert_planned_visit(new_record)
                if new_id is not None:
                    new_record["id"] = new_id
                    new_records.append(new_record)
                    emp_planned.append(
                        f"{store_row.get('StoreName','—')} → {target_sunday.strftime('%d %b %Y')} (Sunday)"
                    )
                else:
                    emp_skipped.append(store_row.get("StoreName", "—"))
            else:
                emp_planned.append(
                    f"{store_row.get('StoreName','—')} → {target_sunday.strftime('%d %b %Y')} (Sunday)"
                )

        summary[ec] = {"name": en, "planned": emp_planned, "skipped": emp_skipped}

    # Update session state with newly inserted records
    if not dry_run and new_records:
        new_df = pd.DataFrame(new_records)
        if "VisitDate" in new_df.columns:
            new_df["VisitDate"] = pd.to_datetime(new_df["VisitDate"], errors="coerce").dt.date
        st.session_state.planned_df = pd.concat(
            [st.session_state.planned_df, new_df], ignore_index=True
        )

    return summary


def run_auto_plan_if_needed():
    """
    Called once per session after login.
    If today > 23, auto-plans all pending stores on next month's Sundays.
    Uses session state flag so it only runs once per session, not on every rerun.
    Safe to call multiple times — get_pending_stores_for_employee() skips already-planned stores.
    """
    if not is_after_cutoff():
        return   # not yet time

    if st.session_state.get("auto_plan_done_month") == date.today().month:
        return   # already ran this session for this month

    # Check if there's anything to plan before running
    emp_df = st.session_state.employee_df
    if emp_df.empty or "EmployeeCode" not in emp_df.columns:
        return

    has_pending = any(
        not get_pending_stores_for_employee(str(erow.get("EmployeeCode", ""))).empty
        for _, erow in emp_df.iterrows()
    )
    if not has_pending:
        st.session_state.auto_plan_done_month = date.today().month
        return

    with st.spinner("🤖 Auto-planning pending stores on next month's Sundays…"):
        result = auto_plan_pending_stores_all_employees(dry_run=False)

    total_planned = sum(len(v.get("planned", [])) for v in result.values() if isinstance(v, dict))
    total_skipped = sum(len(v.get("skipped", [])) for v in result.values() if isinstance(v, dict))

    if total_planned > 0:
        first_sunday = get_next_month_sundays()[0] if get_next_month_sundays() else None
        sun_str = first_sunday.strftime("%d %b %Y") if first_sunday else "next month's Sundays"
        st.toast(
            f"🤖 Auto-plan complete: {total_planned} store(s) scheduled starting {sun_str}."
            + (f" {total_skipped} skipped (slots full)." if total_skipped else ""),
            icon="✅"
        )

    # Mark done for this month so we don't re-run every page load
    st.session_state.auto_plan_done_month = date.today().month

# ====================== NEXT-MONTH DATE INPUT HELPER ======================
def next_month_date_input(label, key, default_to_first=True):
    """
    A date_input restricted to next month only.
    Returns selected date or None if restriction not possible.
    """
    first_day, last_day = get_next_month_range()
    default_val = first_day if default_to_first else min(last_day, first_day + timedelta(days=6))
    # Find first Sunday of next month as default
    d = first_day
    while d <= last_day:
        if d.weekday() == 6:
            default_val = d
            break
        d += timedelta(days=1)

    selected = st.date_input(
        label,
        value=default_val,
        min_value=first_day,
        max_value=last_day,
        key=key,
    )
    return selected

# ====================== LOGIN PAGE ======================
if not st.session_state.logged_in:
    st.markdown("<h1 class='main-header'>🚀 Beat Plan Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Smart Store Visit Planning System</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        login_type = st.radio("Login Type", ["👨‍💼 Admin", "👷 Employee / ASM"], horizontal=True)

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
                        st.error("❌ admin_master columns missing.")
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
                            st.error("❌ Invalid credentials.")
        else:
            st.markdown("### Employee / ASM Login")
            st.caption("Both Employees and Area Sales Managers (ASM) log in here using the same Employee Code.")
            emp_in = st.text_input("Employee Code", key="emp_code_login")
            pwd_in = st.text_input("Password", type="password", key="emp_pwd_login")
            if st.button("🔓 Login", type="primary", use_container_width=True):
                if not emp_in or not pwd_in:
                    st.error("❌ Enter both fields.")
                else:
                    df = st.session_state.employee_df.copy()
                    if "EmployeeCode" not in df.columns or "Password" not in df.columns:
                        st.error("❌ employee_master columns missing.")
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
                            st.session_state.is_asm    = str(match.iloc[0].get("Role", "Employee")).strip() == "ASM"
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials.")
    st.stop()

# ====================== AUTO-PLAN TRIGGER (runs once per session after 23rd) ======================
# Runs for both admin and employee/ASM sessions — safe because get_pending_stores_for_employee
# only returns truly never-planned stores, so already-planned ones are never duplicated.
run_auto_plan_if_needed()

# ====================== LOGOUT ======================
c1, c2, c3 = st.columns([10, 1, 1])
with c3:
    if st.button("🚪 Logout", use_container_width=True):
        for k, v in {
            "logged_in": False, "role": "", "emp_code": "", "emp_name": "",
            "is_asm": False, "selected_cities": [], "auto_plan_done_month": None
        }.items():
            st.session_state[k] = v
        st.rerun()

# ====================== ADMIN PANEL ======================
if st.session_state.role == "admin":
    st.markdown("<h1 class='main-header'>🛠️ Admin Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Beat Plan Pro — Control Center</p>", unsafe_allow_html=True)

    admin_menu = st.sidebar.radio(
        "Navigation",
        ["📊 Dashboard", "📋 Beat Plan Status", "👥 Manage Employees", "🏪 Manage Stores", "📋 View Plans", "🤖 Auto-Plan (After 23rd)", "🔄 Refresh Data"],
    )

    # ── DASHBOARD ──
    if admin_menu == "📊 Dashboard":
        emp_df  = st.session_state.employee_df
        plan_df = st.session_state.planned_df

        with st.spinner("🔄 Checking today's beat plan status from database…"):
            live_status = fetch_beat_status_live(date.today())

        today_emp_codes    = set(live_status.keys())
        total_emp          = len(emp_df)
        done_count         = len(today_emp_codes)
        pending_count      = total_emp - done_count
        today_total_visits = sum(live_status.values())

        cols = st.columns(5)
        cards = [
            ("blue",   "👥", "Total Employees", total_emp,          "Employees + ASM"),
            ("green",  "🏪", "Total Stores",    len(st.session_state.gst_df), "In database"),
            ("purple", "📋", "Total Plans",     len(plan_df),       "All time"),
            ("green",  "✅", "Done Today",      done_count,         "Beat plan submitted"),
            ("red",    "⏳", "Pending Today",   pending_count,      "Yet to submit"),
        ]
        for col, (color, icon, label, val, sub) in zip(cols, cards):
            with col:
                st.markdown(f"""
                    <div class='metric-card {color}'>
                        <div class='metric-icon'>{icon}</div>
                        <div class='metric-label'>{label}</div>
                        <div class='metric-value'>{val}</div>
                        <div class='metric-sub'>{sub}</div>
                    </div>""", unsafe_allow_html=True)

        # Auto-plan notification banner
        if is_after_cutoff():
            first_day, last_day = get_next_month_range()
            sundays = get_next_month_sundays()
            sun_strs = ", ".join([s.strftime("%d %b") for s in sundays])
            st.markdown(f"""
                <div class='warning-banner'>
                    🤖 <strong>Auto-Plan Available!</strong> Today is after the 23rd cutoff.
                    Pending stores can be auto-scheduled on next month's Sundays ({sun_strs}).
                    Go to <strong>🤖 Auto-Plan (After 23rd)</strong> in the sidebar.
                </div>""", unsafe_allow_html=True)

        st.markdown("---")
        col_done, col_pend = st.columns(2)

        with col_done:
            section_header("✅", f"Done — {date.today().strftime('%d %b %Y')} ({done_count})")
            if not today_emp_codes:
                st.info("No submissions yet today.")
            else:
                done_emps = emp_df[emp_df["EmployeeCode"].astype(str).isin(today_emp_codes)] \
                    if "EmployeeCode" in emp_df.columns else pd.DataFrame()
                for _, row in done_emps.iterrows():
                    ec  = str(row.get("EmployeeCode", ""))
                    en  = row.get("EmployeeName", ec)
                    cnt = live_status.get(ec, 0)
                    role_val = str(row.get("Role", "Employee")).strip() or "Employee"
                    role_chip = f"<span class='role-chip {'asm' if role_val=='ASM' else 'emp'}'>{'ASM' if role_val=='ASM' else 'Employee'}</span>"
                    initials = "".join([w[0] for w in en.split()[:2]]).upper()
                    st.markdown(f"""
                        <div class='emp-card'>
                            <div class='emp-avatar done'>{initials}</div>
                            <div class='emp-info'>
                                <div class='emp-name'>{en} {role_chip}</div>
                                <div class='emp-code'>{ec}</div>
                                <div class='emp-count'>🏪 {cnt} store(s) in database</div>
                            </div>
                            <div class='emp-badge badge-done'>✅ Done</div>
                        </div>""", unsafe_allow_html=True)

        with col_pend:
            section_header("⏳", f"Pending — {date.today().strftime('%d %b %Y')} ({pending_count})")
            if "EmployeeCode" in emp_df.columns:
                pend_emps = emp_df[~emp_df["EmployeeCode"].astype(str).isin(today_emp_codes)]
                if pend_emps.empty:
                    st.success("🎉 All employees have submitted today!")
                else:
                    download_pending_button(pend_emps, "pend_dl_dash", date.today())
                    for _, row in pend_emps.iterrows():
                        ec = str(row.get("EmployeeCode", ""))
                        en = row.get("EmployeeName", ec)
                        role_val = str(row.get("Role", "Employee")).strip() or "Employee"
                        role_chip = f"<span class='role-chip {'asm' if role_val=='ASM' else 'emp'}'>{'ASM' if role_val=='ASM' else 'Employee'}</span>"
                        initials = "".join([w[0] for w in en.split()[:2]]).upper()
                        st.markdown(f"""
                            <div class='emp-card'>
                                <div class='emp-avatar pending'>{initials}</div>
                                <div class='emp-info'>
                                    <div class='emp-name'>{en} {role_chip}</div>
                                    <div class='emp-code'>{ec}</div>
                                    <div class='emp-count'>No record found in database</div>
                                </div>
                                <div class='emp-badge badge-pending'>⏳ Pending</div>
                            </div>""", unsafe_allow_html=True)

        st.markdown("---")
        section_header("📦", "Pending Stores — Never Planned (Per Employee/ASM)")
        st.caption("ℹ️ Stores assigned to an employee/ASM that have not been included in ANY beat plan yet (all-time).")
        emp_list = emp_df.copy() if "EmployeeCode" in emp_df.columns else pd.DataFrame()
        if emp_list.empty:
            st.info("No employees found.")
        else:
            summary_rows = []
            all_pending_frames = []
            for _, erow in emp_list.iterrows():
                ec = str(erow.get("EmployeeCode", ""))
                en = erow.get("EmployeeName", ec)
                pend_stores = get_pending_stores_for_employee(ec)
                summary_rows.append({"EmployeeCode": ec, "EmployeeName": en, "PendingStores": len(pend_stores)})
                if not pend_stores.empty:
                    tagged = pend_stores.copy()
                    if "EmployeeCode" not in tagged.columns:
                        tagged.insert(0, "EmployeeCode", ec)
                    else:
                        tagged["EmployeeCode"] = ec
                    if "EmployeeName" not in tagged.columns:
                        tagged.insert(0, "EmployeeName", en)
                    else:
                        tagged["EmployeeName"] = en
                    all_pending_frames.append(tagged)

            summary_df = pd.DataFrame(summary_rows).sort_values("PendingStores", ascending=False)
            total_pending_stores = int(summary_df["PendingStores"].sum())

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                    <div class='metric-card amber'>
                        <div class='metric-icon'>📦</div>
                        <div class='metric-label'>Total Never-Planned Stores</div>
                        <div class='metric-value'>{total_pending_stores}</div>
                        <div class='metric-sub'>Across all employees/ASM</div>
                    </div>""", unsafe_allow_html=True)
            with c2:
                emps_with_pending = int((summary_df["PendingStores"] > 0).sum())
                st.markdown(f"""
                    <div class='metric-card red'>
                        <div class='metric-icon'>👥</div>
                        <div class='metric-label'>Employees With Pending Stores</div>
                        <div class='metric-value'>{emps_with_pending}</div>
                        <div class='metric-sub'>Out of {len(emp_list)} total</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("#### 📊 Employee-wise Pending Store Count")
            st.dataframe(summary_df, use_container_width=True, hide_index=True)

            if all_pending_frames:
                combined_pending = pd.concat(all_pending_frames, ignore_index=True)
                download_pending_stores_button(combined_pending, "all_emp_pend_store_dl", "All_Employees_Pending_Stores")
            else:
                st.success("🎉 Every assigned store has been planned at least once by its employee!")

            st.markdown("#### 📋 Store-level Detail (Per Employee/ASM)")
            for _, erow in emp_list.iterrows():
                ec = str(erow.get("EmployeeCode", ""))
                en = erow.get("EmployeeName", ec)
                pend_stores = get_pending_stores_for_employee(ec)
                if pend_stores.empty:
                    continue
                with st.expander(f"⏳ {en} ({ec}) — {len(pend_stores)} store(s) never planned"):
                    show_cols = [c for c in ["StoreID", "StoreName", "City", "GSTNumber"] if c in pend_stores.columns]
                    st.dataframe(pend_stores[show_cols] if show_cols else pend_stores,
                                 use_container_width=True, hide_index=True)
                    download_pending_stores_button(pend_stores, f"pend_store_dl_{ec}", f"Pending_Stores_{ec}")

        st.markdown("---")
        section_header("📋", "Recent Plans")
        if not plan_df.empty:
            disp = plan_df.drop(columns=["id"], errors="ignore")
            disp = disp.sort_values("VisitDate", ascending=False).head(10) \
                if "VisitDate" in disp.columns else disp.head(10)
            st.dataframe(disp, use_container_width=True, hide_index=True)
        else:
            st.info("No plans yet.")

    # ── BEAT PLAN STATUS ──
    elif admin_menu == "📋 Beat Plan Status":
        st.markdown("### 📋 Beat Plan Status")
        st.caption("ℹ️ Status is fetched live from the database every time you change the date.")

        emp_df   = st.session_state.employee_df
        sel_date = st.date_input("📅 Select Date", value=date.today())

        with st.spinner(f"🔄 Querying database for {sel_date.strftime('%d %b %Y')}…"):
            live_status = fetch_beat_status_live(sel_date)

        date_emp_codes = set(live_status.keys())
        done_n    = len(date_emp_codes)
        pending_n = len(emp_df) - done_n

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
                <div class='metric-card blue'>
                    <div class='metric-icon'>👥</div>
                    <div class='metric-label'>Total Employees</div>
                    <div class='metric-value'>{len(emp_df)}</div>
                </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
                <div class='metric-card green'>
                    <div class='metric-icon'>✅</div>
                    <div class='metric-label'>Submitted</div>
                    <div class='metric-value'>{done_n}</div>
                    <div class='metric-sub'>Records found in DB</div>
                </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
                <div class='metric-card red'>
                    <div class='metric-icon'>⏳</div>
                    <div class='metric-label'>Pending</div>
                    <div class='metric-value'>{pending_n}</div>
                    <div class='metric-sub'>No record in DB</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("---")

        tab_done, tab_pend = st.tabs([
            f"✅ Done ({done_n})",
            f"⏳ Pending ({pending_n})"
        ])

        with tab_done:
            if not date_emp_codes:
                st.info(f"No beat plans found in database for {sel_date.strftime('%d %b %Y')}.")
            else:
                done_emps = emp_df[emp_df["EmployeeCode"].astype(str).isin(date_emp_codes)] \
                    if "EmployeeCode" in emp_df.columns else pd.DataFrame()
                for _, row in done_emps.iterrows():
                    ec  = str(row.get("EmployeeCode", ""))
                    en  = row.get("EmployeeName", ec)
                    cnt = live_status.get(ec, 0)
                    with st.expander(f"✅  {en}  ({ec})  —  {cnt} store(s) in database"):
                        det_df = fetch_emp_plans_live(ec, sel_date)
                        if not det_df.empty:
                            show_cols = [c for c in ["Store","City","GSTNumber","StoreID","VisitDate"] if c in det_df.columns]
                            st.dataframe(det_df[show_cols] if show_cols else det_df,
                                         use_container_width=True, hide_index=True)
                        else:
                            st.info("No store details found.")

        with tab_pend:
            if "EmployeeCode" not in emp_df.columns:
                st.warning("Employee data not loaded.")
            else:
                pend_emps = emp_df[~emp_df["EmployeeCode"].astype(str).isin(date_emp_codes)]
                if pend_emps.empty:
                    st.success(f"🎉 All employees have submitted for {sel_date.strftime('%d %b %Y')}!")
                else:
                    download_pending_button(pend_emps, "pend_dl_status", sel_date)
                    for _, row in pend_emps.iterrows():
                        ec = str(row.get("EmployeeCode", ""))
                        en = row.get("EmployeeName", ec)
                        initials = "".join([w[0] for w in en.split()[:2]]).upper()
                        st.markdown(f"""
                            <div class='emp-card'>
                                <div class='emp-avatar pending'>{initials}</div>
                                <div class='emp-info'>
                                    <div class='emp-name'>{en}</div>
                                    <div class='emp-code'>{ec}</div>
                                    <div class='emp-count'>No record found in database for this date</div>
                                </div>
                                <div class='emp-badge badge-pending'>⏳ Pending</div>
                            </div>""", unsafe_allow_html=True)

    # ── MANAGE EMPLOYEES ──
    elif admin_menu == "👥 Manage Employees":
        st.markdown("### 👥 Manage Employees & ASM")
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
                    epwd  = st.text_input("Password*", type="password")
                    erole = st.selectbox("Role*", ["Employee", "ASM"], help="ASM = Area Sales Manager. ASM stores don't require a GST number.")
                if st.form_submit_button("➕ Add Employee", type="primary"):
                    if not ecode or not ename or not epwd:
                        st.error("All fields required!")
                    elif safe_col(st.session_state.employee_df, "EmployeeCode").astype(str).str.upper().eq(ecode.strip().upper()).any():
                        st.error("❌ Code already exists!")
                    else:
                        new_record = {
                            "EmployeeCode": ecode.strip().upper(),
                            "EmployeeName": ename.strip().title(),
                            "Password": epwd.strip(),
                            "Role": erole,
                        }
                        new_id = insert_employee_row(new_record)
                        if new_id is not None:
                            new_record["id"] = new_id
                            st.session_state.employee_df = pd.concat(
                                [st.session_state.employee_df, pd.DataFrame([new_record])],
                                ignore_index=True
                            )
                            st.success(f"✅ Added as {erole}!")
                            st.rerun()
        with tab3:
            if st.session_state.employee_df.empty:
                st.info("No employees.")
            else:
                emp_del = st.selectbox("Select", safe_col(st.session_state.employee_df, "EmployeeCode").unique())
                if st.button("🗑️ Delete", type="primary"):
                    if delete_employee_row(emp_del):
                        st.session_state.employee_df = st.session_state.employee_df[
                            safe_col(st.session_state.employee_df, "EmployeeCode") != emp_del
                        ].reset_index(drop=True)
                        st.success(f"✅ {emp_del} deleted!")
                        st.rerun()

    # ── MANAGE STORES ──
    elif admin_menu == "🏪 Manage Stores":
        st.markdown("### 🏪 Manage Stores")
        st.caption("ℹ️ GST Number is required for stores assigned to Employees. For ASM, GST is optional (ASM stores often don't have a GST number).")
        tab1, tab2, tab3 = st.tabs(["👁️ View", "➕ Add", "🗑️ Delete"])
        with tab1:
            if not st.session_state.gst_df.empty:
                st.dataframe(st.session_state.gst_df, use_container_width=True, hide_index=True)
            else:
                st.info("No stores found.")
        with tab2:
            emp_opts = safe_col(st.session_state.employee_df, "EmployeeCode").unique().tolist() or ["—"]
            emp_sel = st.selectbox("Assign to Employee/ASM*", emp_opts, key="store_assign_emp")
            assigned_role = get_employee_role(emp_sel)
            gst_required = assigned_role != "ASM"
            if assigned_role == "ASM":
                st.info("ℹ️ This is an ASM — GST Number is optional for this store.")

            with st.form("add_store"):
                c1, c2 = st.columns(2)
                with c1:
                    sname = st.text_input("Store Name*")
                    city  = st.text_input("City*")
                with c2:
                    gstno = st.text_input(
                        f"GST Number{'*' if gst_required else ' (optional for ASM)'}",
                        max_chars=15
                    )
                if st.form_submit_button("➕ Add Store", type="primary"):
                    gc = gstno.strip().upper()
                    if not sname or not city:
                        st.error("Store name and city are required!")
                    elif gst_required and not gc:
                        st.error("❌ GST Number required for stores assigned to an Employee!")
                    elif gc and not is_valid_gstin(gc):
                        st.error("❌ Invalid GST! e.g. 22AAAAA0000A1Z5")
                    elif gc and safe_col(st.session_state.gst_df, "GSTNumber").astype(str).str.upper().eq(gc).any():
                        st.error("❌ GST exists!")
                    else:
                        nid = f"S{len(st.session_state.gst_df)+1:05d}"
                        new_record = {
                            "StoreID": nid,
                            "StoreName": sname.strip().title(),
                            "GSTNumber": gc,  # may be blank for ASM
                            "City": city.strip().title(),
                            "EmployeeCode": emp_sel,
                        }
                        new_id = insert_gst_row(new_record)
                        if new_id is not None:
                            new_record["id"] = new_id
                            st.session_state.gst_df = pd.concat(
                                [st.session_state.gst_df, pd.DataFrame([new_record])],
                                ignore_index=True
                            )
                            st.success("✅ Store added!")
                            st.rerun()
        with tab3:
            if st.session_state.gst_df.empty:
                st.info("No stores.")
            else:
                sdel = st.selectbox("Select Store", safe_col(st.session_state.gst_df, "StoreID").unique())
                if st.button("🗑️ Delete Store", type="primary"):
                    if delete_gst_row(sdel):
                        st.session_state.gst_df = st.session_state.gst_df[
                            safe_col(st.session_state.gst_df, "StoreID") != sdel
                        ].reset_index(drop=True)
                        st.success(f"✅ {sdel} deleted!")
                        st.rerun()

    # ── VIEW PLANS ──
    elif admin_menu == "📋 View Plans":
        st.markdown("### 📋 All Visit Plans")
        c1, c2, c3 = st.columns(3)
        with c1: femp  = st.selectbox("Employee", ["All"] + list(safe_col(st.session_state.planned_df, "EmployeeName").dropna().unique()))
        with c2: fcity = st.selectbox("City",     ["All"] + list(safe_col(st.session_state.planned_df, "City").dropna().unique()))
        with c3: drange = st.date_input("Date Range", value=(date.today()-timedelta(days=30), date.today()))

        fp = st.session_state.planned_df.drop(columns=["id"], errors="ignore").copy()
        if femp  != "All" and "EmployeeName" in fp.columns: fp = fp[fp["EmployeeName"] == femp]
        if fcity != "All" and "City"         in fp.columns: fp = fp[fp["City"]          == fcity]
        if isinstance(drange, (list, tuple)) and len(drange) == 2 and "VisitDate" in fp.columns:
            fp = fp[(fp["VisitDate"] >= drange[0]) & (fp["VisitDate"] <= drange[1])]

        st.markdown(f"**{len(fp)} record(s) found**")

        view_tab1, view_tab2 = st.tabs(["📋 List View", "📊 Beat Plan (Pivot)"])

        with view_tab1:
            st.dataframe(fp.sort_values("VisitDate", ascending=False) if "VisitDate" in fp.columns else fp,
                         use_container_width=True, hide_index=True)
            download_beat_plan_button(fp, "admin_dl", "Beat_Plan_Admin")

        with view_tab2:
            st.caption("ℹ️ One row per employee/store, one column per visit date (1 = planned that day). GST may be blank for ASM stores. Matches the portal's Beat Plan export format.")
            pivot = build_beat_plan_pivot(fp)
            if pivot.empty:
                st.info("No data to pivot for the current filters.")
            else:
                st.dataframe(pivot, use_container_width=True, hide_index=True)

                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    pivot.to_excel(writer, index=False, sheet_name="Beat Plan")
                output.seek(0)
                st.download_button(
                    label="📥 Download Beat Plan (Pivot Excel)",
                    data=output.getvalue(),
                    file_name=f"Beat_Plan_Pivot_{date.today().strftime('%Y-%m-%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="pivot_dl_admin",
                )

    # ── AUTO-PLAN (AFTER 23rd) ──
    elif admin_menu == "🤖 Auto-Plan (After 23rd)":
        st.markdown("### 🤖 Auto-Plan Pending Stores")

        first_day, last_day = get_next_month_range()
        sundays = get_next_month_sundays()
        cutoff_passed = is_after_cutoff()

        # Info banner
        st.markdown(f"""
            <div class='info-banner'>
                📅 <strong>How it works:</strong> After the 23rd of each month, all never-planned stores
                (Employee or ASM) are automatically scheduled on the <strong>Sundays of next month
                ({first_day.strftime('%B %Y')})</strong>.
                Sundays available: {', '.join([s.strftime('%d %b') for s in sundays]) if sundays else 'None found'}.
                Stores are distributed evenly across all available Sundays.
            </div>""", unsafe_allow_html=True)

        if not cutoff_passed:
            days_left = 23 - date.today().day
            st.markdown(f"""
                <div class='warning-banner'>
                    🔒 <strong>Not yet available.</strong> Auto-plan unlocks after the 23rd of each month.
                    <strong>{days_left} day(s)</strong> remaining until cutoff (today is {date.today().strftime('%d %b %Y')}).
                    <br><br>You can still use the <strong>Preview (Dry Run)</strong> below to see what would be scheduled.
                </div>""", unsafe_allow_html=True)

        # Summary of pending stores
        emp_df = st.session_state.employee_df
        total_pending = 0
        emp_pending_summary = []
        if "EmployeeCode" in emp_df.columns:
            for _, erow in emp_df.iterrows():
                ec = str(erow.get("EmployeeCode", ""))
                en = erow.get("EmployeeName", ec)
                ps = get_pending_stores_for_employee(ec)
                total_pending += len(ps)
                emp_pending_summary.append({
                    "EmployeeCode": ec, "EmployeeName": en, "PendingStores": len(ps)
                })

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
                <div class='metric-card amber'>
                    <div class='metric-icon'>📦</div>
                    <div class='metric-label'>Total Pending Stores</div>
                    <div class='metric-value'>{total_pending}</div>
                    <div class='metric-sub'>To be auto-planned</div>
                </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
                <div class='metric-card blue'>
                    <div class='metric-icon'>📅</div>
                    <div class='metric-label'>Available Sundays</div>
                    <div class='metric-value'>{len(sundays)}</div>
                    <div class='metric-sub'>{first_day.strftime('%B %Y')}</div>
                </div>""", unsafe_allow_html=True)
        with c3:
            total_slots = len(sundays) * 10
            st.markdown(f"""
                <div class='metric-card green'>
                    <div class='metric-icon'>🎯</div>
                    <div class='metric-label'>Total Available Slots</div>
                    <div class='metric-value'>{total_slots}</div>
                    <div class='metric-sub'>10 stores × {len(sundays)} Sundays</div>
                </div>""", unsafe_allow_html=True)

        if emp_pending_summary:
            st.markdown("#### 📊 Pending Stores by Employee/ASM")
            st.dataframe(pd.DataFrame(emp_pending_summary).sort_values("PendingStores", ascending=False),
                         use_container_width=True, hide_index=True)

        st.markdown("---")

        col_preview, col_run = st.columns(2)

        with col_preview:
            st.markdown("#### 🔍 Preview (Dry Run)")
            st.caption("See what would be scheduled without actually saving anything.")
            if st.button("🔍 Preview Auto-Plan", use_container_width=True, key="dry_run_btn"):
                with st.spinner("🔄 Calculating preview…"):
                    preview_result = auto_plan_pending_stores_all_employees(dry_run=True)
                if "error" in preview_result:
                    st.error(preview_result["error"])
                else:
                    total_would_plan = sum(len(v["planned"]) for v in preview_result.values())
                    total_would_skip = sum(len(v["skipped"]) for v in preview_result.values())
                    st.success(f"✅ Preview: {total_would_plan} stores would be planned, {total_would_skip} skipped (slots full).")
                    for ec, data in preview_result.items():
                        if data["planned"] or data["skipped"]:
                            with st.expander(f"👤 {data['name']} ({ec}) — {len(data['planned'])} planned, {len(data['skipped'])} skipped"):
                                if data["planned"]:
                                    st.markdown("**Would be planned:**")
                                    for p in data["planned"]:
                                        st.markdown(f"  ✅ {p}")
                                if data["skipped"]:
                                    st.markdown("**Would be skipped (all Sundays full):**")
                                    for s in data["skipped"]:
                                        st.markdown(f"  ⚠️ {s}")

        with col_run:
            st.markdown("#### 🚀 Run Auto-Plan")
            if cutoff_passed:
                st.caption(f"✅ Cutoff passed (today is {date.today().strftime('%d %b')}). Ready to auto-plan.")
                confirm = st.checkbox("✅ I confirm: auto-plan all pending stores on next month's Sundays", key="autoplan_confirm")
                if st.button("🤖 Run Auto-Plan Now", use_container_width=True, key="autoplan_run", disabled=not confirm):
                    with st.spinner("🔄 Auto-planning pending stores…"):
                        result = auto_plan_pending_stores_all_employees(dry_run=False)
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        total_planned = sum(len(v["planned"]) for v in result.values())
                        total_skipped = sum(len(v["skipped"]) for v in result.values())
                        st.success(f"🎉 Done! {total_planned} stores auto-planned across next month's Sundays. {total_skipped} skipped.")
                        for ec, data in result.items():
                            if data["planned"] or data["skipped"]:
                                with st.expander(f"👤 {data['name']} ({ec}) — {len(data['planned'])} planned"):
                                    for p in data["planned"]:
                                        st.markdown(f"  ✅ {p}")
                                    for s in data["skipped"]:
                                        st.markdown(f"  ⚠️ Skipped: {s}")
                        st.rerun()
            else:
                st.caption(f"🔒 Locked until after the 23rd (today is {date.today().strftime('%d %b')}).")
                st.button("🔒 Auto-Plan Locked", disabled=True, use_container_width=True)

    # ── REFRESH ──
    elif admin_menu == "🔄 Refresh Data":
        st.info("Syncs latest data from Supabase.")
        if st.button("🔄 Refresh Now", type="primary", use_container_width=True):
            st.session_state.employee_df = load_from_supabase("employee_master", EMP_COLS)
            st.session_state.gst_df      = load_from_supabase("gst_master",      GST_COLS)
            st.session_state.planned_df  = load_from_supabase("planned_visits",  PLAN_COLS, keep_id=True)
            st.session_state.admin_df    = load_from_supabase("admin_master",    ADMIN_COLS)
            st.success("✅ Refreshed!"); st.rerun()

# ====================== EMPLOYEE / ASM PANEL ======================
else:
    emp_code = st.session_state.emp_code
    emp_name = st.session_state.emp_name
    is_asm   = st.session_state.get("is_asm", False)

    role_label = "🧭 Area Sales Manager" if is_asm else "👤 Employee"
    st.markdown(f"<h1 class='main-header'>{role_label} — {emp_name}</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='sub-header'>Your Beat Planning Dashboard"
        + (" &nbsp;|&nbsp; GST Number not required for ASM stores" if is_asm else "")
        + "</p>",
        unsafe_allow_html=True
    )

    # ── Next-month calendar notice ──
    first_day, last_day = get_next_month_range()
    sundays = get_next_month_sundays()
    sun_strs = ", ".join([s.strftime("%d %b '%y") for s in sundays])
    st.markdown(f"""
        <div class='info-banner'>
            📅 <strong>Planning is open for next month only:</strong>
            {first_day.strftime('%d %b %Y')} – {last_day.strftime('%d %b %Y')} &nbsp;|&nbsp;
            🗓️ Sundays: {sun_strs}
        </div>""", unsafe_allow_html=True)

    pending_all = get_pending_stores_for_employee(emp_code)
    render_pending_marquee(pending_all)

    if not pending_all.empty:
        with st.expander(f"📦 Quick Plan a Never-Planned Store ({len(pending_all)} available)", expanded=False):
            store_options = {
                f"{r.get('StoreName','—')} — {r.get('City','—')} ({r.get('StoreID','—')})": r.get("StoreID", "")
                for _, r in pending_all.iterrows()
            }
            colA, colB, colC = st.columns([3, 2, 1])
            with colA:
                sel_label = st.selectbox("Select store", list(store_options.keys()), key="marquee_quick_store")
            with colB:
                # RESTRICTED to next month only
                marquee_plan_date = next_month_date_input("📅 Plan for date", key="marquee_plan_date")
            with colC:
                st.markdown("<br>", unsafe_allow_html=True)
                confirm_clicked = st.button("✅ Plan It", key="marquee_confirm", use_container_width=True)

            if confirm_clicked:
                sel_sid = store_options.get(sel_label)
                match_row = pending_all[safe_col(pending_all, "StoreID").astype(str) == str(sel_sid)]
                if match_row.empty:
                    st.error("❌ Store not found. Refresh and try again.")
                else:
                    row = match_row.iloc[0]
                    day_count = len(st.session_state.planned_df[
                        (safe_col(st.session_state.planned_df, "EmployeeCode").astype(str) == str(emp_code)) &
                        (st.session_state.planned_df["VisitDate"] == marquee_plan_date)
                    ]) if "VisitDate" in st.session_state.planned_df.columns else 0

                    if day_count >= 10:
                        st.error(f"🚫 {marquee_plan_date.strftime('%d %b %Y')} already has 10 stores planned. Pick another date.")
                    else:
                        new_record = {
                            "EmployeeCode": emp_code,
                            "EmployeeName": emp_name,
                            "City":         row.get("City", ""),
                            "Store":        row.get("StoreName", ""),
                            "StoreID":      row.get("StoreID", ""),
                            "GSTNumber":    row.get("GSTNumber", ""),
                            "VisitDate":    marquee_plan_date,
                        }
                        new_id = insert_planned_visit(new_record)
                        if new_id is not None:
                            new_record["id"] = new_id
                            new_record["VisitDate"] = marquee_plan_date
                            st.session_state.planned_df = pd.concat(
                                [st.session_state.planned_df, pd.DataFrame([new_record])],
                                ignore_index=True
                            )
                            st.success(f"✅ {row.get('StoreName','')} planned for {marquee_plan_date.strftime('%d %b %Y')}!")
                            st.rerun()

    employee_stores = st.session_state.gst_df[
        safe_col(st.session_state.gst_df, "EmployeeCode").astype(str) == str(emp_code)
    ] if not st.session_state.gst_df.empty else pd.DataFrame(columns=GST_COLS)

    emp_menu = st.sidebar.radio(
        "Navigation",
        ["🎯 New Beat Plan", "📦 Pending Stores", "📅 My Plans", "📆 Upcoming Plans", "📊 Analytics", "➕ Request New Store"],
    )

    # ── NEW BEAT PLAN ──
    if emp_menu == "🎯 New Beat Plan":
        if employee_stores.empty:
            st.warning("⚠️ No stores assigned. Contact Admin.")
            st.stop()

        c1, c2, c3 = st.columns(3)
        with c1:
            # RESTRICTED: only next month's dates
            visit_date = next_month_date_input("📅 Date (Next Month Only)", key="beat_date")
        with c2:
            city_opts  = sorted(safe_col(employee_stores, "City").dropna().unique().tolist())
            sel_cities = st.multiselect("🌍 Cities (max 3)", city_opts, max_selections=3, key="city_ms")
        with c3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔍 Load Stores", use_container_width=True):
                st.session_state.selected_cities = sel_cities

        # Validate the selected date is in next month (safety check)
        if not (first_day <= visit_date <= last_day):
            st.error(f"🚫 Please select a date within next month ({first_day.strftime('%d %b')} – {last_day.strftime('%d %b %Y')}).")
            st.stop()

        daily_plans = st.session_state.planned_df[
            (safe_col(st.session_state.planned_df, "EmployeeCode").astype(str) == str(emp_code)) &
            (st.session_state.planned_df["VisitDate"] == visit_date)
        ] if "VisitDate" in st.session_state.planned_df.columns else pd.DataFrame(columns=PLAN_COLS)

        pc   = len(daily_plans)
        pcol = get_progress_color(pc, 10)

        st.markdown(f"""
            <div class='progress-wrap'>
                <div style='display:flex;justify-content:space-between;'>
                    <span class='progress-label'>Daily Progress — {visit_date.strftime('%d %b %Y')} ({visit_date.strftime('%A')})</span>
                    <span style='font-weight:800;color:{pcol};font-size:18px;'>{pc}/10</span>
                </div>
                <div class='progress-track'>
                    <div class='progress-fill' style='width:{min(pc*10,100)}%;background:{pcol};'></div>
                </div>
                <div style='font-size:13px;color:#64748b;'>
                    {"🚫 Maximum 10 stores reached." if pc >= 10 else f"✅ {10-pc} more store(s) can be added for this date."}
                </div>
            </div>""", unsafe_allow_html=True)

        search_query = st.text_input("🔍 Search stores by name, city or GST…", key="store_search", placeholder="e.g. Sharma Medical, Lucknow, 09AAA…")

        show_cities = st.session_state.selected_cities or safe_col(employee_stores, "City").unique().tolist()
        city_stores = employee_stores[safe_col(employee_stores, "City").isin(show_cities)]
        planned_ids = safe_col(daily_plans, "StoreID").tolist()
        available   = city_stores[~safe_col(city_stores, "StoreID").isin(planned_ids)]

        if search_query.strip():
            q = search_query.strip().lower()
            mask = (
                safe_col(available, "StoreName").str.lower().str.contains(q, na=False) |
                safe_col(available, "City").str.lower().str.contains(q, na=False) |
                safe_col(available, "GSTNumber").str.lower().str.contains(q, na=False)
            )
            available = available[mask]

        if not daily_plans.empty:
            with st.expander(f"✅ Planned stores for {visit_date.strftime('%d %b %Y')} ({pc})"):
                show = [c for c in ["Store","City","GSTNumber"] if c in daily_plans.columns]
                st.dataframe(daily_plans[show], use_container_width=True, hide_index=True)

        if pc < 10:
            section_header("🏪", f"Available Stores ({len(available)})")
            if available.empty:
                st.info("No stores found. Try a different search or city.")
            else:
                for idx, row in available.iterrows():
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f"""
                            <div class='store-card'>
                                <div class='store-name'>🏪 {row.get('StoreName','—')}</div>
                                <div class='store-meta'>
                                    <span class='store-chip'>📍 {row.get('City','—')}</span>
                                    <span class='store-chip'>🪪 {row.get('StoreID','—')}</span>
                                    {gst_chip_html(row)}
                                </div>
                            </div>""", unsafe_allow_html=True)
                    with col2:
                        st.markdown("<br><br>", unsafe_allow_html=True)
                        if st.button("➕ Add", key=f"add_{idx}_{visit_date}"):
                            new_record = {
                                "EmployeeCode": emp_code,
                                "EmployeeName": emp_name,
                                "City":         row.get("City", ""),
                                "Store":        row.get("StoreName", ""),
                                "StoreID":      row.get("StoreID", ""),
                                "GSTNumber":    row.get("GSTNumber", ""),
                                "VisitDate":    visit_date,
                            }
                            new_id = insert_planned_visit(new_record)
                            if new_id is not None:
                                new_record["id"] = new_id
                                new_record["VisitDate"] = visit_date
                                st.session_state.planned_df = pd.concat(
                                    [st.session_state.planned_df, pd.DataFrame([new_record])],
                                    ignore_index=True
                                )
                                st.success(f"✅ {row.get('StoreName','')} added!")
                                st.rerun()

        st.markdown("---")
        emp_plans = st.session_state.planned_df[
            safe_col(st.session_state.planned_df, "EmployeeCode").astype(str) == str(emp_code)]
        download_beat_plan_button(emp_plans, "emp_dl", f"Beat_Plan_{emp_code}")

    # ── PENDING STORES (never planned) ──
    elif emp_menu == "📦 Pending Stores":
        st.markdown("### 📦 Pending Stores")
        st.caption("ℹ️ Stores assigned to you that have not been included in ANY beat plan yet (all-time). GST may be blank for ASM stores.")

        pend_stores = get_pending_stores_for_employee(emp_code)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
                <div class='metric-card blue'>
                    <div class='metric-icon'>🏪</div>
                    <div class='metric-label'>Total Assigned Stores</div>
                    <div class='metric-value'>{len(employee_stores)}</div>
                </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
                <div class='metric-card red'>
                    <div class='metric-icon'>📦</div>
                    <div class='metric-label'>Never Planned</div>
                    <div class='metric-value'>{len(pend_stores)}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("---")

        if pend_stores.empty:
            st.success("🎉 You've planned every assigned store at least once!")
        else:
            col_search, col_date = st.columns([3, 2])
            with col_search:
                search_q = st.text_input("🔍 Search pending stores…", key="pend_store_search", placeholder="Store name, city, GST…")
            with col_date:
                # RESTRICTED: only next month's dates
                plan_for_date = next_month_date_input("📅 Plan for date (Next Month)", key="pend_store_plan_date")

            view_df = pend_stores.copy()
            if search_q.strip():
                q = search_q.strip().lower()
                mask = (
                    safe_col(view_df, "StoreName").str.lower().str.contains(q, na=False) |
                    safe_col(view_df, "City").str.lower().str.contains(q, na=False) |
                    safe_col(view_df, "GSTNumber").str.lower().str.contains(q, na=False)
                )
                view_df = view_df[mask]

            existing_on_date = st.session_state.planned_df[
                (safe_col(st.session_state.planned_df, "EmployeeCode").astype(str) == str(emp_code)) &
                (st.session_state.planned_df["VisitDate"] == plan_for_date)
            ] if "VisitDate" in st.session_state.planned_df.columns else pd.DataFrame()
            slots_left = 10 - len(existing_on_date)

            section_header("📦", f"Never-Planned Stores ({len(view_df)})")
            st.caption(f"📅 Adding to **{plan_for_date.strftime('%A, %d %b %Y')}** — {max(slots_left,0)} slot(s) left that day (max 10/day).")

            for idx, row in view_df.iterrows():
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f"""
                        <div class='store-card'>
                            <div class='store-name'>🏪 {row.get('StoreName','—')}</div>
                            <div class='store-meta'>
                                <span class='store-chip'>📍 {row.get('City','—')}</span>
                                <span class='store-chip'>🪪 {row.get('StoreID','—')}</span>
                                {gst_chip_html(row)}
                            </div>
                        </div>""", unsafe_allow_html=True)
                with col2:
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    if slots_left <= 0:
                        st.button("🚫 Full", key=f"plan_pending_{idx}", disabled=True)
                    elif st.button("➕ Plan", key=f"plan_pending_{idx}"):
                        new_record = {
                            "EmployeeCode": emp_code,
                            "EmployeeName": emp_name,
                            "City":         row.get("City", ""),
                            "Store":        row.get("StoreName", ""),
                            "StoreID":      row.get("StoreID", ""),
                            "GSTNumber":    row.get("GSTNumber", ""),
                            "VisitDate":    plan_for_date,
                        }
                        new_id = insert_planned_visit(new_record)
                        if new_id is not None:
                            new_record["id"] = new_id
                            new_record["VisitDate"] = plan_for_date
                            st.session_state.planned_df = pd.concat(
                                [st.session_state.planned_df, pd.DataFrame([new_record])],
                                ignore_index=True
                            )
                            st.success(f"✅ {row.get('StoreName','')} added to {plan_for_date.strftime('%d %b %Y')}!")
                            st.rerun()

            st.markdown("---")
            download_pending_stores_button(pend_stores, "emp_pend_store_dl", f"Pending_Stores_{emp_code}")

    # ── MY PLANS (with delete) ──
    elif emp_menu == "📅 My Plans":
        my = st.session_state.planned_df[
            safe_col(st.session_state.planned_df, "EmployeeCode").astype(str) == str(emp_code)].copy()

        if my.empty:
            st.info("No plans yet.")
        else:
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Total Plans",  len(my))
            with c2: st.metric("Cities",       safe_col(my, "City").nunique())
            with c3: st.metric("Unique Dates", len(safe_col(my, "VisitDate").unique()))

            st.markdown("---")

            col_f1, col_f2 = st.columns(2)
            with col_f1:
                del_search = st.text_input("🔍 Search my plans…", placeholder="Store name, city…", key="my_plan_search")
            with col_f2:
                # Admin can view any date; employees see next month's filter defaulted
                date_filter = st.date_input("📅 Filter by date", value=first_day, key="my_plan_date")
                use_date    = st.checkbox("Apply date filter", key="my_plan_use_date")

            filtered = my.copy()
            if del_search.strip():
                q = del_search.strip().lower()
                mask = (
                    safe_col(filtered, "Store").str.lower().str.contains(q, na=False) |
                    safe_col(filtered, "City").str.lower().str.contains(q, na=False)
                )
                filtered = filtered[mask]
            if use_date and "VisitDate" in filtered.columns:
                filtered = filtered[filtered["VisitDate"] == date_filter]

            section_header("📋", f"My Plans ({len(filtered)})")

            if filtered.empty:
                st.info("No plans match the filter.")
            else:
                for i, (idx, row) in enumerate(filtered.iterrows()):
                    col_info, col_del = st.columns([6, 1])
                    with col_info:
                        vd = row.get("VisitDate", "")
                        vd_str = vd.strftime("%d %b %Y") if hasattr(vd, "strftime") else str(vd)
                        gst_disp = str(row.get('GSTNumber', '') or '').strip()
                        gst_line = f" &nbsp;|&nbsp; 🧾 {gst_disp}" if gst_disp and gst_disp.lower() not in ("nan", "none") else ""
                        st.markdown(f"""
                            <div class='del-row'>
                                <div style='font-size:24px;'>🏪</div>
                                <div class='del-info'>
                                    <div style='font-weight:700;font-size:15px;'>{row.get('Store','—')}</div>
                                    <div class='del-date'>📍 {row.get('City','—')}{gst_line} &nbsp;|&nbsp; 📅 {vd_str}</div>
                                </div>
                            </div>""", unsafe_allow_html=True)
                    with col_del:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("🗑️", key=f"del_plan_{idx}_{i}", help="Remove this entry"):
                            row_id = row.get("id")
                            if row_id and str(row_id).lower() not in ("", "nan", "none"):
                                if delete_planned_visit(row_id):
                                    st.session_state.planned_df = st.session_state.planned_df.drop(index=idx).reset_index(drop=True)
                                    st.success("✅ Entry removed.")
                                    st.rerun()
                            else:
                                st.session_state.planned_df = st.session_state.planned_df.drop(index=idx).reset_index(drop=True)
                                st.warning("⚠️ Removed from session. DB row may persist — refresh data to sync.")
                                st.rerun()

            st.markdown("---")
            download_beat_plan_button(my, "my_dl", f"My_Plans_{emp_code}")

    # ── UPCOMING PLANS ──
    elif emp_menu == "📆 Upcoming Plans":
        if "VisitDate" not in st.session_state.planned_df.columns:
            st.info("No upcoming visits.")
        else:
            upcoming = st.session_state.planned_df[
                (safe_col(st.session_state.planned_df, "EmployeeCode").astype(str) == str(emp_code)) &
                (st.session_state.planned_df["VisitDate"] >= first_day)
            ].sort_values("VisitDate")
            if upcoming.empty:
                st.info(f"No upcoming visits planned for next month ({first_day.strftime('%B %Y')}).")
            else:
                for vdate in sorted(upcoming["VisitDate"].unique()):
                    plans = upcoming[upcoming["VisitDate"] == vdate]
                    is_sunday = vdate.weekday() == 6
                    label = "🔵 Sunday" if is_sunday else ""
                    st.markdown(f"""
                        <div style='background:#f0f9ff;border-left:4px solid #1a56db;
                             padding:12px 16px;border-radius:10px;margin-bottom:8px;'>
                            <strong>📅 {vdate.strftime('%A, %d %B %Y')}</strong>
                            &nbsp;<span style='color:#1a56db;font-size:13px;font-weight:600;'>{label}</span>
                            &nbsp;— {len(plans)} store(s)
                        </div>""", unsafe_allow_html=True)
                    for _, p in plans.iterrows():
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;• **{p.get('Store','—')}** — {p.get('City','—')}")

    # ── ANALYTICS ──
    elif emp_menu == "📊 Analytics":
        my = st.session_state.planned_df[
            safe_col(st.session_state.planned_df, "EmployeeCode").astype(str) == str(emp_code)]
        if my.empty:
            st.info("No data yet.")
        else:
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.metric("Total Visits", len(my))
            with c2: st.metric("Cities",       safe_col(my, "City").nunique())
            with c3: st.metric("Stores",       safe_col(my, "Store").nunique())
            with c4:
                nm = my[pd.to_datetime(safe_col(my, "VisitDate"), errors="coerce").dt.month == first_day.month] \
                    if "VisitDate" in my.columns else pd.DataFrame()
                st.metric(f"Next Month ({first_day.strftime('%b')})", len(nm))
            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Visits by City")
                if "City" in my.columns: st.bar_chart(my.groupby("City").size())
            with c2:
                st.subheader("Visits Over Time")
                if "VisitDate" in my.columns:
                    tmp = my.copy()
                    tmp["Month"] = pd.to_datetime(tmp["VisitDate"], errors="coerce").dt.to_period("M").astype(str)
                    st.line_chart(tmp.groupby("Month").size())

    # ── REQUEST NEW STORE ──
    elif emp_menu == "➕ Request New Store":
        st.subheader("➕ Add New Store")
        if is_asm:
            st.caption("ℹ️ As an ASM, GST Number is optional for your stores.")
        with st.form("store_req"):
            c1, c2 = st.columns(2)
            with c1:
                sname = st.text_input("Store Name*")
                city  = st.text_input("City*")
            with c2:
                gst = st.text_input(f"GST Number{'*' if not is_asm else ' (optional)'}", max_chars=15)
                _   = st.text_area("Remarks (optional)", height=100)
            if st.form_submit_button("✅ Add Store", type="primary"):
                gc = gst.strip().upper()
                if not sname or not city:
                    st.error("❌ Store name and city are required!")
                elif not is_asm and not gc:
                    st.error("❌ GST Number required!")
                elif gc and not is_valid_gstin(gc):
                    st.error("❌ Invalid GST! e.g. 22AAAAA0000A1Z5")
                elif gc and safe_col(st.session_state.gst_df, "GSTNumber").astype(str).str.upper().eq(gc).any():
                    st.error("❌ GST exists!")
                else:
                    nid = f"S{len(st.session_state.gst_df)+1:05d}"
                    new_record = {
                        "StoreID": nid,
                        "StoreName": sname.strip().title(),
                        "GSTNumber": gc,  # may be blank for ASM
                        "City": city.strip().title(),
                        "EmployeeCode": emp_code,
                    }
                    new_id = insert_gst_row(new_record)
                    if new_id is not None:
                        new_record["id"] = new_id
                        st.session_state.gst_df = pd.concat(
                            [st.session_state.gst_df, pd.DataFrame([new_record])],
                            ignore_index=True
                        )
                        st.success(f"✅ '{sname.title()}' added!")
                        st.rerun()

# ====================== FOOTER ======================
st.markdown("---")
st.caption("Beat Plan Pro © 2026 | 🚀 Created By Bipin Pandey")
