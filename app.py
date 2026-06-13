import streamlit as st
import pandas as pd
from datetime import date, timedelta
import re
import io
from supabase import create_client, Client
import json

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="Beat Plan Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="auto"
)

# ====================== DEVICE DETECTION ======================
st.markdown("""
<script>
window.deviceType = (function() {
    const ua = navigator.userAgent;
    const isTablet = /iPad|Android(?!.*Mobile)|Tablet/i.test(ua);
    const isMobile = /Mobile|iPhone|Android|Opera Mini/i.test(ua);
    const isLandscape = window.innerWidth > window.innerHeight;
    
    if (isMobile && !isTablet) return 'mobile';
    if (isTablet) return 'tablet';
    return 'desktop';
})();
window.isLandscape = window.innerWidth > window.innerHeight;
</script>
""", unsafe_allow_html=True)

# ====================== SUPABASE CONFIG ======================
SUPABASE_URL = "https://kueicdruccvbempjvxzn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt1ZWljZHJ1Y2N2YmVtcGp2eHpuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODExMjE0MTcsImV4cCI6MjA5NjY5NzQxN30.aWkQ85Wq-iP2Gp1W1dfoATdRhR0rFcc1H6CGtK_zDE0"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"❌ Failed to connect to Supabase: {e}")
    st.stop()

# ====================== COMPREHENSIVE RESPONSIVE STYLING ======================
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    html, body, .stApp {
        width: 100%;
        height: 100%;
        overflow-x: hidden;
    }
    
    .stApp { 
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        max-width: 100%;
    }
    
    /* ===== DESKTOP (1024px+) ===== */
    @media (min-width: 1024px) {
        [data-testid="stMainBlockContainer"] {
            padding: 24px !important;
            max-width: 1400px;
        }
        
        .main-header {
            font-size: 48px;
            margin: 20px 0 10px 0;
        }
        
        .sub-header {
            font-size: 16px;
            margin-bottom: 30px;
        }
        
        .metric-card {
            padding: 24px;
            margin-bottom: 16px;
        }
        
        .store-card {
            padding: 20px;
            margin-bottom: 12px;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 16px;
        }
        
        [data-testid="stRadio"] {
            flex-direction: row;
            gap: 20px;
        }
    }
    
    /* ===== TABLET (768px - 1023px) ===== */
    @media (min-width: 768px) and (max-width: 1023px) {
        [data-testid="stMainBlockContainer"] {
            padding: 16px !important;
        }
        
        .main-header {
            font-size: 36px;
            margin: 16px 0 8px 0;
        }
        
        .sub-header {
            font-size: 15px;
            margin-bottom: 20px;
        }
        
        .metric-card {
            padding: 18px;
            margin-bottom: 12px;
        }
        
        .store-card {
            padding: 16px;
            margin-bottom: 10px;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
        }
        
        [data-testid="stRadio"] {
            flex-direction: row;
            gap: 12px;
            flex-wrap: wrap;
        }
    }
    
    /* ===== MOBILE (max 767px) ===== */
    @media (max-width: 767px) {
        [data-testid="stMainBlockContainer"] {
            padding: 8px !important;
        }
        
        [data-testid="stSidebar"] {
            width: 100% !important;
        }
        
        .main-header {
            font-size: 28px;
            margin: 12px 0 6px 0;
            line-height: 1.2;
        }
        
        .sub-header {
            font-size: 13px;
            margin-bottom: 16px;
        }
        
        .metric-card {
            padding: 14px;
            margin-bottom: 10px;
        }
        
        .store-card {
            padding: 14px;
            margin-bottom: 10px;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 10px 12px !important;
            font-size: 12px !important;
        }
        
        [data-testid="stRadio"] {
            flex-direction: column;
            gap: 10px;
        }
        
        /* Stack form inputs vertically */
        .stSelectbox, .stTextInput, .stDateInput, .stMultiSelect {
            margin-bottom: 8px !important;
        }
    }
    
    /* ===== LANDSCAPE MODE (max-height: 600px) ===== */
    @media (orientation: landscape) and (max-height: 600px) {
        .main-header {
            font-size: 20px !important;
            margin: 4px 0 !important;
        }
        
        .sub-header {
            display: none;
        }
        
        [data-testid="stMainBlockContainer"] {
            padding: 4px !important;
        }
        
        .metric-card, .store-card {
            padding: 8px !important;
            margin-bottom: 4px !important;
        }
    }
    
    /* ===== UNIVERSAL STYLES ===== */
    .main-header {
        font-weight: 900;
        background: linear-gradient(90deg, #0066cc, #00a8e8, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        letter-spacing: -1px;
    }
    
    .sub-header {
        text-align: center;
        color: #475569;
        font-weight: 600;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
    }
    
    .metric-card:active {
        transform: scale(0.98);
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }
    
    .store-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 12px;
        border-left: 4px solid #0066cc;
        border: 2px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
    }
    
    .store-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .progress-section {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 16px;
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        margin-bottom: 16px;
    }
    
    .metric-value {
        font-weight: 800;
        background: linear-gradient(135deg, #0066cc, #00a8e8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 8px;
        font-size: clamp(20px, 6vw, 36px);
    }
    
    .metric-label {
        color: #64748b;
        font-weight: 600;
        margin-bottom: 6px;
        font-size: clamp(11px, 3vw, 14px);
    }
    
    .icon {
        font-size: clamp(20px, 8vw, 32px);
        margin-bottom: 8px;
    }
    
    /* ===== BUTTONS ===== */
    .stButton > button {
        border-radius: 10px;
        min-height: 44px;
        font-weight: 700;
        background: linear-gradient(90deg, #0066cc, #00a8e8) !important;
        color: white !important;
        border: none !important;
        font-size: clamp(12px, 3vw, 14px) !important;
        width: 100%;
        touch-action: manipulation;
        transition: all 0.2s ease;
    }
    
    .stButton > button:active {
        transform: scale(0.95);
    }
    
    /* ===== INPUT FIELDS ===== */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stMultiSelect > div > div > select,
    .stDateInput > div > div > input,
    .stTextArea > div > div > textarea {
        font-size: 16px !important;
        padding: 12px !important;
        border-radius: 8px !important;
        border: 2px solid #e2e8f0 !important;
        min-height: 44px !important;
        width: 100% !important;
    }
    
    .stTextArea > div > div > textarea {
        min-height: 100px !important;
    }
    
    /* ===== INFO BOXES ===== */
    .info-box {
        background: #f0f9ff;
        border-left: 4px solid #0066cc;
        padding: 12px;
        border-radius: 8px;
        font-size: clamp(12px, 3vw, 14px);
        margin-bottom: 12px;
    }
    
    .success-box {
        background: #f0fdf4;
        border-left: 4px solid #10b981;
        padding: 12px;
        border-radius: 8px;
        font-size: clamp(12px, 3vw, 14px);
        margin-bottom: 12px;
    }
    
    .warning-box {
        background: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 12px;
        border-radius: 8px;
        font-size: clamp(12px, 3vw, 14px);
        margin-bottom: 12px;
    }
    
    .error-box {
        background: #fef2f2;
        border-left: 4px solid #ef4444;
        padding: 12px;
        border-radius: 8px;
        font-size: clamp(12px, 3vw, 14px);
        margin-bottom: 12px;
    }
    
    /* ===== DATAFRAME ===== */
    [data-testid="dataFrameContainer"] {
        font-size: clamp(11px, 2.5vw, 13px) !important;
        overflow-x: auto;
    }
    
    /* ===== EXPANDER ===== */
    [data-testid="stExpander"] {
        border-radius: 8px !important;
    }
    
    /* ===== TABS ===== */
    [data-baseweb="tab"] {
        font-size: clamp(12px, 3vw, 14px) !important;
        padding: 12px 16px !important;
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
        st.error(f"❌ Connection failed: {e}")
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
        st.error(f"❌ Save failed: {e}")
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
            label="📥 Download Excel",
            data=output.getvalue(),
            file_name=f"{filename_prefix}_{date.today().strftime('%Y-%m-%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key=key,
        )

# ====================== LOGIN PAGE ======================
if not st.session_state.logged_in:
    st.markdown("<h1 class='main-header'>🚀 Beat Plan Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Smart Store Visit Planning</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        login_type = st.radio("Select Role", ["👨‍💼 Admin", "👷 Employee"], horizontal=False, key="login_type")

        if login_type == "👨‍💼 Admin":
            st.markdown("### Admin Login")
            with st.form("admin_login_form"):
                user = st.text_input("👤 Username", placeholder="Enter username", key="admin_user")
                pwd  = st.text_input("🔒 Password", type="password", placeholder="••••••••", key="admin_pwd")
                submit = st.form_submit_button("🔓 Login", type="primary", use_container_width=True)
                
                if submit:
                    if not user or not pwd:
                        st.error("❌ Enter both fields.")
                    else:
                        df = st.session_state.admin_df.copy()
                        if "Username" not in df.columns or "Password" not in df.columns:
                            st.error("❌ Database error. Contact support.")
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
                                st.error(f"❌ Invalid credentials.")
        else:
            st.markdown("### Employee Login")
            with st.form("emp_login_form"):
                emp_in = st.text_input("🏷️ Employee Code", placeholder="Enter code", key="emp_code_login")
                pwd_in = st.text_input("🔒 Password", type="password", placeholder="••••••••", key="emp_pwd_login")
                submit = st.form_submit_button("🔓 Login", type="primary", use_container_width=True)
                
                if submit:
                    if not emp_in or not pwd_in:
                        st.error("❌ Enter both fields.")
                    else:
                        df = st.session_state.employee_df.copy()
                        if "EmployeeCode" not in df.columns or "Password" not in df.columns:
                            st.error("❌ Database error. Contact support.")
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
                                st.error(f"❌ Invalid credentials.")
    st.stop()

# ====================== LOGOUT & HEADER ======================
col1, col2, col3 = st.columns([10, 1, 1])
with col3:
    if st.button("🚪", help="Logout", use_container_width=True):
        for k, v in {"logged_in": False, "role": "", "emp_code": "", "emp_name": "", "selected_cities": []}.items():
            st.session_state[k] = v
        st.rerun()

# ====================== ADMIN PANEL ======================
if st.session_state.role == "admin":
    st.markdown("<h1 class='main-header'>🛠️ Admin Dashboard</h1>", unsafe_allow_html=True)

    admin_menu = st.sidebar.radio(
        "📍 Navigation",
        ["📊 Dashboard", "👥 Employees", "🏪 Stores", "📋 Plans", "🔄 Refresh"],
        key="admin_nav"
    )

    if admin_menu == "📊 Dashboard":
        today_plans = int((st.session_state.planned_df["VisitDate"] == date.today()).sum()) \
            if "VisitDate" in st.session_state.planned_df.columns else 0

        cols = st.columns([1, 1])
        metrics = [
            ("👥", "Employees", len(st.session_state.employee_df)),
            ("🏪", "Stores",    len(st.session_state.gst_df)),
            ("📋", "Plans",     len(st.session_state.planned_df)),
            ("📅", "Today",     today_plans),
        ]
        for i, (icon, label, val) in enumerate(metrics):
            with cols[i % 2]:
                st.markdown(f"""
                    <div class='metric-card'>
                        <div class='icon'>{icon}</div>
                        <div class='metric-label'>{label}</div>
                        <div class='metric-value'>{val}</div>
                    </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("📋 Recent Plans")
        if not st.session_state.planned_df.empty:
            recent = st.session_state.planned_df.sort_values("VisitDate", ascending=False).head(5) \
                if "VisitDate" in st.session_state.planned_df.columns else st.session_state.planned_df.head(5)
            st.dataframe(recent, use_container_width=True, hide_index=True)
        else:
            st.info("No plans yet.")

    elif admin_menu == "👥 Employees":
        tab1, tab2, tab3 = st.tabs(["👁️ View", "➕ Add", "🗑️ Delete"])
        
        with tab1:
            disp = st.session_state.employee_df.drop(columns=["Password"], errors="ignore")
            if not disp.empty:
                st.dataframe(disp, use_container_width=True, hide_index=True)
            else:
                st.info("No employees found.")
                
        with tab2:
            st.subheader("Add New Employee")
            with st.form("add_emp"):
                ecode = st.text_input("Employee Code", placeholder="EMP001", key="emp_code_add")
                ename = st.text_input("Employee Name", placeholder="John Doe", key="emp_name_add")
                epwd = st.text_input("Password", type="password", placeholder="••••••••", key="emp_pwd_add")
                if st.form_submit_button("➕ Add Employee", type="primary", use_container_width=True):
                    if not ecode or not ename or not epwd:
                        st.error("❌ All fields required!")
                    elif safe_col(st.session_state.employee_df, "EmployeeCode").astype(str).str.upper().eq(ecode.strip().upper()).any():
                        st.error("❌ Code already exists!")
                    else:
                        new_row = pd.DataFrame([{"EmployeeCode": ecode.strip().upper(), "EmployeeName": ename.strip().title(), "Password": epwd.strip()}])
                        st.session_state.employee_df = pd.concat([st.session_state.employee_df, new_row], ignore_index=True)
                        if save_to_supabase("employee_master", st.session_state.employee_df):
                            st.success("✅ Employee added!"); st.rerun()
                            
        with tab3:
            st.subheader("Delete Employee")
            if st.session_state.employee_df.empty:
                st.info("No employees.")
            else:
                emp_del = st.selectbox("Select Employee", safe_col(st.session_state.employee_df, "EmployeeCode").unique())
                if st.button("🗑️ Delete", type="primary", use_container_width=True):
                    st.session_state.employee_df = st.session_state.employee_df[
                        safe_col(st.session_state.employee_df, "EmployeeCode") != emp_del]
                    if save_to_supabase("employee_master", st.session_state.employee_df):
                        st.success(f"✅ Deleted!"); st.rerun()

    elif admin_menu == "🏪 Stores":
        tab1, tab2, tab3 = st.tabs(["👁️ View", "➕ Add", "🗑️ Delete"])
        
        with tab1:
            if not st.session_state.gst_df.empty:
                st.dataframe(st.session_state.gst_df, use_container_width=True, hide_index=True)
            else:
                st.info("No stores found.")
                
        with tab2:
            st.subheader("Add New Store")
            with st.form("add_store"):
                sname = st.text_input("Store Name", placeholder="ABC Store", key="store_name")
                gstno = st.text_input("GST Number", placeholder="22AAAAA0000A1Z5", max_chars=15, key="gst_input")
                city  = st.text_input("City", placeholder="Mumbai", key="city_input")
                emp_opts = safe_col(st.session_state.employee_df, "EmployeeCode").unique().tolist() or ["—"]
                emp_sel  = st.selectbox("Assign Employee", emp_opts, key="emp_assign")
                if st.form_submit_button("➕ Add Store", type="primary", use_container_width=True):
                    gc = gstno.strip().upper()
                    if not sname or not gc or not city:
                        st.error("❌ All fields required!")
                    elif not is_valid_gstin(gc):
                        st.error("❌ Invalid GST format!")
                    elif safe_col(st.session_state.gst_df, "GSTNumber").astype(str).str.upper().eq(gc).any():
                        st.error("❌ GST exists!")
                    else:
                        nid = f"S{len(st.session_state.gst_df)+1:05d}"
                        st.session_state.gst_df = pd.concat([st.session_state.gst_df,
                            pd.DataFrame([{"StoreID": nid, "StoreName": sname.strip().title(),
                                           "GSTNumber": gc, "City": city.strip().title(), "EmployeeCode": emp_sel}])
                        ], ignore_index=True)
                        if save_to_supabase("gst_master", st.session_state.gst_df):
                            st.success("✅ Store added!"); st.rerun()
                            
        with tab3:
            st.subheader("Delete Store")
            if st.session_state.gst_df.empty:
                st.info("No stores.")
            else:
                sdel = st.selectbox("Select Store", safe_col(st.session_state.gst_df, "StoreID").unique())
                if st.button("🗑️ Delete", type="primary", use_container_width=True):
                    st.session_state.gst_df = st.session_state.gst_df[safe_col(st.session_state.gst_df, "StoreID") != sdel]
                    if save_to_supabase("gst_master", st.session_state.gst_df):
                        st.success("✅ Deleted!"); st.rerun()

    elif admin_menu == "📋 Plans":
        st.subheader("All Visit Plans")
        c1, c2 = st.columns(2)
        with c1: femp  = st.selectbox("Employee", ["All"] + list(safe_col(st.session_state.planned_df, "EmployeeName").dropna().unique()))
        with c2: fcity = st.selectbox("City",     ["All"] + list(safe_col(st.session_state.planned_df, "City").dropna().unique()))
        
        drange = st.date_input("Date Range", value=(date.today()-timedelta(days=30), date.today()))

        fp = st.session_state.planned_df.copy()
        if femp  != "All" and "EmployeeName" in fp.columns: fp = fp[fp["EmployeeName"] == femp]
        if fcity != "All" and "City"         in fp.columns: fp = fp[fp["City"]          == fcity]
        if isinstance(drange, (list, tuple)) and len(drange) == 2 and "VisitDate" in fp.columns:
            fp = fp[(fp["VisitDate"] >= drange[0]) & (fp["VisitDate"] <= drange[1])]

        st.markdown(f"**{len(fp)} record(s)**")
        st.dataframe(fp.sort_values("VisitDate", ascending=False) if "VisitDate" in fp.columns else fp,
                     use_container_width=True, hide_index=True)
        download_beat_plan_button(fp, "admin_dl", "Beat_Plan_Admin")

    elif admin_menu == "🔄 Refresh":
        st.subheader("Sync Data")
        st.markdown("Pull latest data from database.")
        if st.button("🔄 Refresh Now", type="primary", use_container_width=True):
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
    st.markdown("<p class='sub-header'>Beat Planning Dashboard</p>", unsafe_allow_html=True)

    employee_stores = st.session_state.gst_df[
        safe_col(st.session_state.gst_df, "EmployeeCode").astype(str) == str(emp_code)
    ] if not st.session_state.gst_df.empty else pd.DataFrame(columns=GST_COLS)

    emp_menu = st.sidebar.radio(
        "📍 Navigation",
        ["🎯 New Plan", "📅 My Plans", "📆 Upcoming", "📊 Analytics", "➕ New Store"],
        key="emp_nav"
    )

    if emp_menu == "🎯 New Plan":
        if employee_stores.empty:
            st.warning("⚠️ No stores assigned. Contact Admin.")
            st.stop()

        st.subheader("Create Beat Plan")
        c1, c2 = st.columns(2)
        with c1: visit_date = st.date_input("📅 Date", value=date.today(), key="beat_date")
        with c2:
            city_opts = sorted(safe_col(employee_stores, "City").dropna().unique().tolist())
            sel_cities = st.multiselect("🌍 Cities (max 3)", city_opts, max_selections=3, key="city_ms")

        if st.button("🔍 Load Stores", use_container_width=True):
            st.session_state.selected_cities = sel_cities

        daily_plans = st.session_state.planned_df[
            (safe_col(st.session_state.planned_df, "EmployeeCode").astype(str) == str(emp_code)) &
            (st.session_state.planned_df["VisitDate"] == visit_date)
        ] if "VisitDate" in st.session_state.planned_df.columns else pd.DataFrame(columns=PLAN_COLS)

        pc    = len(daily_plans)
        pcol  = get_progress_color(pc, 10)

        st.markdown(f"""
            <div class='progress-section'>
                <div style='display:flex;justify-content:space-between;margin-bottom:10px;'>
                    <span style='font-weight:700;'>Progress</span>
                    <span style='font-weight:800;color:{pcol};'>{pc}/10</span>
                </div>
                <div style='height:12px;background:#e2e8f0;border-radius:10px;overflow:hidden;'>
                    <div style='width:{min(pc*10,100)}%;height:100%;background:{pcol};transition:width 0.3s;'></div>
                </div>
                <div style='margin-top:8px;color:#64748b;font-size:13px;font-weight:500;'>
                    {"🚫 Max 10 reached" if pc >= 10 else f"✅ {10-pc} slot(s) left"}
                </div>
            </div>""", unsafe_allow_html=True)

        if not daily_plans.empty:
            with st.expander(f"✅ Planned for {visit_date} ({pc})"):
                show = [c for c in ["Store","City","GSTNumber"] if c in daily_plans.columns]
                st.dataframe(daily_plans[show], use_container_width=True, hide_index=True)

        if pc < 10:
            show_cities = st.session_state.selected_cities or safe_col(employee_stores, "City").unique().tolist()
            city_stores = employee_stores[safe_col(employee_stores, "City").isin(show_cities)]
            planned_ids = safe_col(daily_plans, "StoreID").tolist()
            available   = city_stores[~safe_col(city_stores, "StoreID").isin(planned_ids)]

            st.markdown(f"### 🛍️ Available ({len(available)})")
            if available.empty:
                st.info("No more stores available.")
            else:
                for idx, row in available.iterrows():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"""
                            <div class='store-card'>
                                <strong>🏪 {row.get('StoreName','—')}</strong><br/>
                                <span style='color:#64748b;font-size:12px;'>
                                    📍 {row.get('City','—')} • GST: {row.get('GSTNumber','—')[:8]}...
                                </span>
                            </div>""", unsafe_allow_html=True)
                    with col2:
                        if st.button("➕", key=f"add_{idx}", help="Add store", use_container_width=True):
                            new_plan = pd.DataFrame([{
                                "EmployeeCode": emp_code, "EmployeeName": emp_name,
                                "City": row.get("City",""), "Store": row.get("StoreName",""),
                                "StoreID": row.get("StoreID",""), "GSTNumber": row.get("GSTNumber",""),
                                "VisitDate": visit_date,
                            }])
                            st.session_state.planned_df = pd.concat(
                                [st.session_state.planned_df, new_plan], ignore_index=True)
                            if save_to_supabase("planned_visits", st.session_state.planned_df):
                                st.success("✅ Added!"); st.rerun()

        st.markdown("---")
        emp_plans = st.session_state.planned_df[
            safe_col(st.session_state.planned_df, "EmployeeCode").astype(str) == str(emp_code)]
        download_beat_plan_button(emp_plans, "emp_dl", f"Beat_Plan_{emp_code}")

    elif emp_menu == "📅 My Plans":
        st.subheader("All Your Plans")
        my = st.session_state.planned_df[
            safe_col(st.session_state.planned_df, "EmployeeCode").astype(str) == str(emp_code)]
        if my.empty:
            st.info("No plans yet.")
        else:
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Total", len(my))
            with c2: st.metric("Cities", safe_col(my,"City").nunique())
            with c3: st.metric("Dates", len(safe_col(my,"VisitDate").unique()))
            st.dataframe(my.sort_values("VisitDate",ascending=False) if "VisitDate" in my.columns else my,
                         use_container_width=True, hide_index=True)
            download_beat_plan_button(my, "my_dl", f"My_Plans_{emp_code}")

    elif emp_menu == "📆 Upcoming":
        st.subheader("Upcoming Visits")
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
                    label = "🟢 TODAY" if vdate == date.today() else "⭕ " + vdate.strftime("%a")
                    st.markdown(f"""
                        <div class='info-box' style='margin-bottom:12px;'>
                            <strong>📅 {vdate.strftime('%d %b %Y')}</strong> - {label}
                            <br/><span style='font-size:12px;color:#64748b;'>{len(plans)} store(s)</span>
                        </div>""", unsafe_allow_html=True)
                    for _, p in plans.iterrows():
                        st.markdown(f"&nbsp;&nbsp;&nbsp;🏪 **{p.get('Store','—')}** • {p.get('City','—')}")

    elif emp_menu == "📊 Analytics":
        st.subheader("Your Statistics")
        my = st.session_state.planned_df[
            safe_col(st.session_state.planned_df,"EmployeeCode").astype(str) == str(emp_code)]
        if my.empty:
            st.info("No data yet.")
        else:
            c1, c2, c3, c4 = st.columns(2)
            with c1: st.metric("Total Visits", len(my))
            with c2: st.metric("Cities", safe_col(my,"City").nunique())
            with c3: st.metric("Stores", safe_col(my,"Store").nunique())
            with c4:
                tm = my[pd.to_datetime(safe_col(my,"VisitDate"),errors="coerce").dt.month == date.today().month] \
                    if "VisitDate" in my.columns else pd.DataFrame()
                st.metric("This Month", len(tm))
            
            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**📍 By City**")
                if "City" in my.columns and not my.empty: 
                    st.bar_chart(my.groupby("City").size())
            with c2:
                st.markdown("**📅 Over Time**")
                if "VisitDate" in my.columns and not my.empty:
                    tmp = my.copy()
                    tmp["Month"] = pd.to_datetime(tmp["VisitDate"],errors="coerce").dt.to_period("M").astype(str)
                    st.line_chart(tmp.groupby("Month").size())

    elif emp_menu == "➕ New Store":
        st.subheader("Request New Store")
        with st.form("store_req"):
            sname = st.text_input("Store Name", placeholder="ABC Store", key="req_store_name")
            city  = st.text_input("City", placeholder="Mumbai", key="req_city")
            gst   = st.text_input("GST Number", placeholder="22AAAAA0000A1Z5", max_chars=15, key="req_gst")
            notes = st.text_area("Remarks (optional)", placeholder="Additional details...", height=80, key="req_notes")
            
            if st.form_submit_button("✅ Request", type="primary", use_container_width=True):
                gc = gst.strip().upper()
                if not sname or not city or not gc:
                    st.error("❌ All fields required!")
                elif not is_valid_gstin(gc):
                    st.error("❌ Invalid GST format!")
                elif safe_col(st.session_state.gst_df,"GSTNumber").astype(str).str.upper().eq(gc).any():
                    st.error("❌ GST already exists!")
                else:
                    nid = f"S{len(st.session_state.gst_df)+1:05d}"
                    st.session_state.gst_df = pd.concat([st.session_state.gst_df,
                        pd.DataFrame([{"StoreID":nid,"StoreName":sname.strip().title(),
                                       "GSTNumber":gc,"City":city.strip().title(),"EmployeeCode":emp_code}])
                    ], ignore_index=True)
                    if save_to_supabase("gst_master", st.session_state.gst_df):
                        st.success(f"✅ {sname.title()} added!"); st.rerun()

st.markdown("---")
st.caption("Beat Plan Pro © 2026 | Created by Bipin Pandey | Fully Responsive v2.1")
