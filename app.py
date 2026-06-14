import streamlit as st
import pandas as pd
from datetime import date, timedelta
import re, io, datetime as dt_mod
from supabase import create_client, Client

# ── Page config ──────────────────────────────────────────
st.set_page_config(page_title="Beat Plan Pro", page_icon="🗺️",
                   layout="wide", initial_sidebar_state="collapsed")

# ── Supabase ─────────────────────────────────────────────
SUPABASE_URL = "https://kueicdruccvbempjvxzn.supabase.co"
SUPABASE_KEY = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
                "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt1ZWljZHJ1Y2N2YmVtcGp2eHpuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODExMjE0MTcsImV4cCI6MjA5NjY5NzQxN30."
                "aWkQ85Wq-iP2Gp1W1dfoATdRhR0rFcc1H6CGtK_zDE0")
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"Supabase error: {e}"); st.stop()


# ── CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
*,*::before,*::after{box-sizing:border-box;}
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;}
.stApp{background:#f4f6fb!important;}
#MainMenu,footer,header{visibility:hidden;}
[data-testid="collapsedControl"],[data-testid="stSidebar"]{display:none!important;}

/* ═══════ DESKTOP (≥769px) ═══════ */
.block-container{padding:0 0 60px 0!important;max-width:1160px!important;margin:0 auto!important;}

.desk-nav{
  background:#fff;border-bottom:1px solid #e2e5ef;
  padding:0 32px;display:flex;align-items:center;height:62px;gap:4px;
  position:sticky;top:0;z-index:999;box-shadow:0 2px 12px rgba(0,0,0,.05);
  margin-bottom:24px;
}
.dn-logo{display:flex;align-items:center;gap:9px;font-size:16px;font-weight:800;
  color:#18181b;letter-spacing:-.3px;margin-right:18px;white-space:nowrap;}
.dn-logo-icon{width:32px;height:32px;border-radius:9px;
  background:linear-gradient(135deg,#4f46e5,#7c3aed);
  display:flex;align-items:center;justify-content:center;font-size:16px;
  box-shadow:0 2px 8px rgba(79,70,229,.28);}
.dn-links{display:flex;gap:2px;flex:1;}
.dn-btn{padding:7px 14px;border-radius:10px;font-size:13px;font-weight:500;
  border:1px solid transparent;background:transparent;color:#6b7280;
  cursor:pointer;transition:all .15s;white-space:nowrap;}
.dn-btn:hover{background:#f4f6fb;color:#374151;}
.dn-btn.active{background:#4f46e5;color:#fff;border-color:#4f46e5;
  box-shadow:0 2px 8px rgba(79,70,229,.28);}
.dn-right{display:flex;align-items:center;gap:9px;margin-left:auto;}
.dn-avatar{width:34px;height:34px;border-radius:50%;
  background:linear-gradient(135deg,#4f46e5,#06b6d4);
  color:#fff;font-size:12px;font-weight:700;
  display:flex;align-items:center;justify-content:center;flex-shrink:0;}
.dn-name{font-size:13px;font-weight:600;color:#374151;}
.dn-role{font-size:10.5px;padding:2px 9px;border-radius:20px;font-weight:600;background:#eef2ff;color:#4338ca;}

.page-pad{padding:0 32px;}

.stat-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-bottom:22px;}

/* ═══════ MOBILE (≤768px) ═══════ */
@media(max-width:768px){
  .block-container{padding:0 0 88px 0!important;max-width:100%!important;}
  .desk-nav{display:none!important;}
  .mob-header{display:flex!important;}
  .mob-bot-nav{display:flex!important;}
  .mob-bot-btns{display:flex!important;}
  .page-pad{padding:0 14px!important;}
  .stat-grid{grid-template-columns:1fr 1fr!important;gap:10px!important;}
  .two-col{grid-template-columns:1fr!important;}
  .qa-row{grid-template-columns:1fr 1fr!important;gap:10px!important;}
  .stButton>button{height:52px!important;font-size:15px!important;border-radius:14px!important;}
  .stTextInput>div>div>input{height:52px!important;font-size:15px!important;padding:14px 16px!important;}
  .stSelectbox>div>div{min-height:52px!important;font-size:15px!important;}
  .stDateInput>div>div>input{height:52px!important;font-size:15px!important;}
  .stMultiSelect>div>div{min-height:52px!important;}
}

/* Mobile header */
.mob-header{display:none;position:sticky;top:0;z-index:999;background:#fff;
  border-bottom:1px solid #e2e5ef;padding:13px 16px 10px;
  align-items:center;justify-content:space-between;
  box-shadow:0 2px 12px rgba(0,0,0,.06);margin-bottom:0;}
.mob-logo{display:flex;align-items:center;gap:8px;font-size:16px;font-weight:800;color:#18181b;}
.mob-logo-icon{width:30px;height:30px;border-radius:8px;
  background:linear-gradient(135deg,#4f46e5,#7c3aed);
  display:flex;align-items:center;justify-content:center;font-size:15px;}
.mob-av{width:32px;height:32px;border-radius:50%;
  background:linear-gradient(135deg,#4f46e5,#06b6d4);
  color:#fff;font-size:11px;font-weight:700;
  display:flex;align-items:center;justify-content:center;}

/* Mobile bottom nav */
.mob-bot-nav{display:none;position:fixed;bottom:0;left:0;right:0;z-index:999;
  background:#fff;border-top:1px solid #e2e5ef;
  justify-content:space-around;align-items:center;
  padding:6px 0 10px;box-shadow:0 -4px 20px rgba(0,0,0,.08);}
.mbn-item{display:flex;flex-direction:column;align-items:center;gap:2px;
  font-size:10px;font-weight:500;color:#9ca3af;flex:1;text-align:center;}
.mbn-item.active{color:#4f46e5;}
.mbn-icon{font-size:22px;line-height:1;}

.mob-bot-btns{display:none;position:fixed;bottom:0;left:0;right:0;z-index:1000;height:64px;}
.mob-bot-btns .stButton>button{
  border-radius:0!important;height:64px!important;
  background:transparent!important;color:transparent!important;
  box-shadow:none!important;border:none!important;font-size:1px!important;}

/* ═══════ SHARED COMPONENTS ═══════ */
.greeting{background:linear-gradient(135deg,#4f46e5,#7c3aed);
  border-radius:20px;padding:24px;color:#fff;margin-bottom:20px;}
.g-hi{font-size:22px;font-weight:800;margin-bottom:4px;}
.g-sub{font-size:13.5px;opacity:.85;}
.g-date{font-size:12px;opacity:.65;margin-top:8px;}

.stat-card{background:#fff;border:1px solid #e2e5ef;border-radius:16px;
  padding:18px 18px 14px;position:relative;overflow:hidden;
  box-shadow:0 2px 10px rgba(0,0,0,.04);transition:transform .15s,box-shadow .15s;}
.stat-card:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(0,0,0,.08);}
.s-top{position:absolute;top:0;left:0;width:100%;height:3px;}
.s-ico{font-size:22px;margin-bottom:10px;}
.s-val{font-size:26px;font-weight:800;color:#18181b;letter-spacing:-1px;line-height:1;}
.s-lbl{font-size:12px;color:#9ca3af;margin-top:3px;font-weight:500;}
.s-ft{font-size:11.5px;font-weight:600;margin-top:9px;padding-top:8px;border-top:1px solid #f4f6fb;}

.card{background:#fff;border:1px solid #e2e5ef;border-radius:16px;
  padding:18px 20px;box-shadow:0 2px 10px rgba(0,0,0,.04);margin-bottom:14px;}
.card-hdr{display:flex;align-items:center;gap:9px;font-size:14px;font-weight:700;color:#18181b;
  padding-bottom:12px;margin-bottom:14px;border-bottom:1px solid #f4f6fb;}
.card-hdr-ico{width:28px;height:28px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:14px;}
.card-pill{font-size:11px;padding:3px 9px;border-radius:20px;font-weight:600;margin-left:auto;}

.two-col{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:14px;}
.qa-row{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-bottom:18px;}
.qa-card{background:#fff;border:1px solid #e2e5ef;border-radius:16px;
  padding:18px 16px;display:flex;flex-direction:column;gap:8px;
  box-shadow:0 2px 8px rgba(0,0,0,.04);transition:all .15s;}
.qa-card:hover{transform:translateY(-2px);box-shadow:0 6px 18px rgba(0,0,0,.08);border-color:#c7d2fe;}
.qa-ico{width:40px;height:40px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:20px;}
.qa-lbl{font-size:13.5px;font-weight:700;color:#18181b;}
.qa-dsc{font-size:12px;color:#9ca3af;}

.sec-hd{font-size:15px;font-weight:700;color:#18181b;
  margin:18px 0 10px;display:flex;align-items:center;gap:7px;}
.sec-ct{font-size:11px;background:#f0f2f8;color:#6b7280;padding:2px 8px;border-radius:20px;font-weight:600;}

.prog-row{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;}
.prog-lbl{font-size:13px;font-weight:600;color:#374151;}
.prog-num{font-size:13px;font-weight:700;}
.prog-track{height:8px;background:#f0f2f8;border-radius:99px;overflow:hidden;margin-bottom:6px;}
.prog-fill{height:100%;border-radius:99px;}
.prog-hint{font-size:12px;color:#9ca3af;}

.si{display:flex;align-items:center;gap:12px;padding:12px 14px;
  border-radius:14px;background:#f9fafb;border:1px solid #f0f2f8;
  margin-bottom:8px;transition:all .15s;}
.si:hover{background:#f0f2f8;border-color:#e2e5ef;}
.si-av{width:38px;height:38px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:17px;flex-shrink:0;}
.av-i{background:#eef2ff;}.av-g{background:#f0fdf4;}.av-r{background:#fef2f2;}.av-a{background:#fffbeb;}
.si-nm{font-size:13.5px;font-weight:600;color:#18181b;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.si-mt{font-size:12px;color:#9ca3af;margin-top:2px;}

.bdg{font-size:11px;padding:4px 10px;border-radius:20px;font-weight:600;white-space:nowrap;flex-shrink:0;}
.bg{background:#dcfce7;color:#15803d;}.br{background:#fee2e2;color:#b91c1c;}
.ba{background:#fef9c3;color:#854d0e;}.bp{background:#ede9fe;color:#6d28d9;}
.bb{background:#dbeafe;color:#1d4ed8;}

.tl{display:flex;gap:12px;align-items:flex-start;padding:12px 14px;
  border-radius:14px;background:#f9fafb;border:1px solid #f0f2f8;margin-bottom:8px;}
.tl-date{width:44px;flex-shrink:0;text-align:center;border-radius:12px;padding:7px 3px;}
.tl-date.tod{background:linear-gradient(135deg,#4f46e5,#7c3aed);box-shadow:0 3px 10px rgba(79,70,229,.28);}
.tl-date.fut{background:#fff;border:1px solid #e2e5ef;}
.tl-day{font-size:19px;font-weight:800;line-height:1;}
.tl-mon{font-size:9px;text-transform:uppercase;letter-spacing:.06em;margin-top:2px;}
.tl-date.tod .tl-day,.tl-date.tod .tl-mon{color:#fff;}
.tl-date.fut .tl-day{color:#18181b;}.tl-date.fut .tl-mon{color:#9ca3af;}
.tl-tt{font-size:13.5px;font-weight:700;color:#18181b;margin-bottom:2px;}
.tl-sb{font-size:12px;color:#9ca3af;margin-bottom:5px;}
.tl-pl{display:flex;flex-wrap:wrap;gap:4px;}
.tl-p{font-size:11px;background:#fff;border:1px solid #e2e5ef;color:#4b5563;padding:2px 7px;border-radius:20px;}

.ib{background:#eef2ff;border:1px solid #c7d2fe;border-radius:12px;
  padding:12px 16px;font-size:13px;color:#3730a3;margin-bottom:14px;line-height:1.6;}
.wb{background:#fffbeb;border:1px solid #fcd34d;border-radius:12px;
  padding:12px 16px;font-size:13px;color:#92400e;margin-bottom:14px;line-height:1.6;}

.pt{font-size:22px;font-weight:800;color:#18181b;letter-spacing:-.5px;margin-bottom:2px;}
.ps{font-size:13px;color:#9ca3af;margin-bottom:18px;}

.emp{text-align:center;padding:48px 20px;}
.emp-ico{font-size:44px;margin-bottom:12px;}
.emp-tt{font-size:15px;font-weight:700;color:#374151;margin-bottom:4px;}
.emp-sb{font-size:13px;color:#9ca3af;line-height:1.6;}

.lg-wrap{max-width:430px;margin:0 auto;padding:32px 20px;}
.lg-top{text-align:center;margin-bottom:28px;}
.lg-ico{width:66px;height:66px;border-radius:20px;
  background:linear-gradient(135deg,#4f46e5,#7c3aed);
  display:inline-flex;align-items:center;justify-content:center;
  font-size:30px;color:#fff;margin-bottom:16px;
  box-shadow:0 8px 24px rgba(79,70,229,.3);}
.lg-tt{font-size:25px;font-weight:800;color:#18181b;letter-spacing:-.5px;}
.lg-sb{font-size:14px;color:#9ca3af;margin-top:5px;}
.lg-lbl{font-size:13px;font-weight:600;color:#374151;margin-bottom:5px;}

/* Streamlit overrides */
.stButton>button{border-radius:12px!important;height:44px!important;
  font-weight:700!important;font-size:14px!important;
  background:#4f46e5!important;color:#fff!important;border:none!important;
  box-shadow:0 3px 10px rgba(79,70,229,.22)!important;transition:all .15s!important;}
.stButton>button:hover{background:#4338ca!important;
  box-shadow:0 5px 16px rgba(79,70,229,.35)!important;transform:translateY(-1px)!important;}
.stButton>button:active{transform:scale(.98)!important;}
.stTextInput>div>div>input{border-radius:11px!important;border:1.5px solid #e2e5ef!important;
  font-size:14px!important;background:#fafbff!important;padding:11px 14px!important;}
.stTextInput>div>div>input:focus{border-color:#4f46e5!important;background:#fff!important;
  box-shadow:0 0 0 3px rgba(79,70,229,.1)!important;}
.stTextInput>div>div>input::placeholder{color:#c4c9d9!important;}
.stSelectbox>div>div,.stMultiSelect>div>div{border-radius:11px!important;
  border:1.5px solid #e2e5ef!important;background:#fafbff!important;}
.stDateInput>div>div>input{border-radius:11px!important;border:1.5px solid #e2e5ef!important;}
.stTextArea>div>div>textarea{border-radius:11px!important;border:1.5px solid #e2e5ef!important;
  font-size:14px!important;background:#fafbff!important;padding:12px 14px!important;}
.stTabs [data-baseweb="tab-list"]{gap:4px;background:#f0f2f8;border-radius:12px;
  padding:4px;border:none!important;}
.stTabs [data-baseweb="tab"]{border-radius:9px!important;font-size:13px!important;
  font-weight:600!important;padding:8px 18px!important;color:#6b7280!important;
  background:transparent!important;border:none!important;}
.stTabs [aria-selected="true"]{background:#fff!important;color:#4f46e5!important;
  font-weight:700!important;box-shadow:0 1px 6px rgba(0,0,0,.08)!important;}
.stDataFrame{border-radius:14px!important;border:1px solid #e2e5ef!important;overflow:hidden!important;}
.stAlert{border-radius:12px!important;font-size:13.5px!important;}
.stDownloadButton>button{background:#f9fafb!important;color:#374151!important;
  border:1.5px solid #e2e5ef!important;border-radius:12px!important;
  font-weight:600!important;box-shadow:none!important;}
.stDownloadButton>button:hover{background:#f0f2f8!important;transform:none!important;}
.streamlit-expanderHeader{background:#f9fafb!important;border-radius:12px!important;
  font-size:13.5px!important;font-weight:600!important;
  border:1px solid #e2e5ef!important;color:#374151!important;}
hr{border-color:#e2e5ef!important;margin:16px 0!important;}
.stTextInput label,.stSelectbox label,.stMultiSelect label,
.stDateInput label,.stTextArea label{font-size:13px!important;font-weight:600!important;color:#374151!important;}
[data-testid="stMetric"]{background:#fff!important;border:1px solid #e2e5ef!important;
  border-radius:14px!important;padding:16px!important;}
</style>
""", unsafe_allow_html=True)


# ── DB helpers ────────────────────────────────────────────
COLUMN_MAP = {
    "EmployeeCode":["employeecode","employee_code"],
    "EmployeeName":["employeename","employee_name"],
    "Password":["password"],"StoreID":["storeid","store_id"],
    "StoreName":["storename","store_name"],"GSTNumber":["gstnumber","gst_number"],
    "City":["city"],"Store":["store"],"VisitDate":["visitdate","visit_date"],
    "Username":["username"],
}

def normalize_columns(df):
    rename={}; lower_map={c.lower().replace("_",""):c for c in df.columns}
    for exp,variants in COLUMN_MAP.items():
        if exp in df.columns: continue
        for v in variants:
            k=v.lower().replace("_","")
            if k in lower_map: rename[lower_map[k]]=exp; break
    return df.rename(columns=rename) if rename else df

def init_db():
    try: supabase.table("planned_visits").select("*").limit(1).execute(); return True
    except Exception as e: st.error(f"Supabase: {e}"); return False

def clean_df(df, cols):
    if df.empty: return df
    df=normalize_columns(df)
    for c in cols:
        if c not in df.columns: df[c]=""
    for c in df.select_dtypes(include=["object"]).columns:
        df[c]=df[c].astype(str).str.strip()
    if "VisitDate" in df.columns:
        df["VisitDate"]=pd.to_datetime(df["VisitDate"],errors="coerce").dt.date
    return df

def load_sb(table, columns):
    try:
        rows,bs,off=[],1000,0
        while True:
            r=supabase.table(table).select("*").range(off,off+bs-1).execute()
            if not r.data: break
            rows.extend(r.data)
            if len(r.data)<bs: break
            off+=bs
        return clean_df(pd.DataFrame(rows),columns) if rows else pd.DataFrame(columns=columns)
    except Exception as e:
        st.warning(f"Load error {table}: {e}"); return pd.DataFrame(columns=columns)

def sanitize(df):
    import math; d=df.copy()
    for c in d.columns:
        if pd.api.types.is_float_dtype(d[c]):
            d[c]=d[c].apply(lambda x: None if (x is None or (isinstance(x,float) and (math.isnan(x) or math.isinf(x)))) else x)
        elif d[c].dtype==object:
            d[c]=d[c].apply(lambda x: None if (x is None or (isinstance(x,str) and x.lower() in ("nan","none",""))) else x)
    return d.where(pd.notnull(d),None)

def save_sb(table, df):
    try:
        d=df.copy()
        if "id" in d.columns: d=d.drop("id",axis=1)
        for c in d.columns:
            if c=="VisitDate" or pd.api.types.is_datetime64_any_dtype(d[c]):
                d[c]=pd.to_datetime(d[c],errors="coerce").dt.strftime("%Y-%m-%d")
        d=sanitize(d)
        try: supabase.table(table).delete().neq("id",-1).execute()
        except: pass
        if not d.empty:
            recs=[{k:v for k,v in r.items() if v is not None} for r in d.to_dict("records")]
            for i in range(0,len(recs),100): supabase.table(table).insert(recs[i:i+100]).execute()
        return True
    except Exception as e: st.error(f"Save error: {e}"); return False

# ── Constants ─────────────────────────────────────────────
EC=["EmployeeCode","EmployeeName","Password"]
GC=["StoreID","StoreName","GSTNumber","City","EmployeeCode"]
PC=["EmployeeCode","EmployeeName","City","Store","GSTNumber","StoreID","VisitDate"]
AC=["Username","Password"]

# ── Init session ──────────────────────────────────────────
if not init_db(): st.stop()
for key,loader in [
    ("edf",lambda:load_sb("employee_master",EC)),
    ("gdf",lambda:load_sb("gst_master",GC)),
    ("pdf",lambda:load_sb("planned_visits",PC)),
    ("adf",lambda:load_sb("admin_master",AC)),
]:
    if key not in st.session_state: st.session_state[key]=loader()

DEF={"li":False,"role":"","ec":"","en":"","pg":"Home","sc":[]}
for k,v in DEF.items():
    if k not in st.session_state: st.session_state[k]=v

# ── Utility functions ─────────────────────────────────────
def gstin_ok(g):
    return bool(re.match(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$",str(g).strip().upper()))

def sc(df,col):
    return df[col] if col in df.columns else pd.Series([""]*len(df))

def ini(name):
    p=str(name).strip().split()
    return (p[0][0]+p[-1][0]).upper() if len(p)>=2 else name[:2].upper()

def pc_color(n): return "#4f46e5" if n<8 else "#f59e0b" if n<10 else "#ef4444"

def go(p): st.session_state.pg=p; st.rerun()

def dl_btn(df,key,prefix="Beat_Plan"):
    if not df.empty:
        out=io.BytesIO()
        with pd.ExcelWriter(out,engine="openpyxl") as w: df.to_excel(w,index=False,sheet_name="Beat Plan")
        out.seek(0)
        st.download_button("⬇  Export Excel",data=out.getvalue(),
            file_name=f"{prefix}_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,key=key)

def stat_cards(items):
    h="<div class='stat-grid'>"
    for top,ico,val,lbl,ft,fc in items:
        h+=f"<div class='stat-card'><div class='s-top' style='background:{top}'></div><div class='s-ico'>{ico}</div><div class='s-val'>{val}</div><div class='s-lbl'>{lbl}</div><div class='s-ft' style='color:{fc};'>{ft}</div></div>"
    h+="</div>"; st.markdown(h,unsafe_allow_html=True)

def empty(ico,tt,sb=""):
    st.markdown(f"<div class='emp'><div class='emp-ico'>{ico}</div><div class='emp-tt'>{tt}</div><div class='emp-sb'>{sb}</div></div>",unsafe_allow_html=True)

def ib(msg): st.markdown(f"<div class='ib'>ℹ️  {msg}</div>",unsafe_allow_html=True)
def wb(msg): st.markdown(f"<div class='wb'>⚠️  {msg}</div>",unsafe_allow_html=True)
def phdr(t,s=""): st.markdown(f"<div class='pt'>{t}</div>{'<div class=ps>'+s+'</div>' if s else ''}",unsafe_allow_html=True)

def render_shell(name,role,page):
    av=ini(name); rl="Admin" if role=="admin" else "Employee"
    emp_nav=["Home","Beat Plan","My Plans","Upcoming","Analytics"]
    adm_nav=["Home","Employees","Stores","View Plans","Refresh"]
    nav=adm_nav if role=="admin" else emp_nav
    icons={"Home":"🏠","Beat Plan":"🎯","My Plans":"📅","Upcoming":"📆",
           "Analytics":"📈","Employees":"👥","Stores":"🏪","View Plans":"📋","Refresh":"🔄"}

    # Desktop top nav
    btns="".join(f'<button class="dn-btn{" active" if page==p else ""}">{icons.get(p,"")} {p}</button>' for p in nav)
    st.markdown(f"""
    <div class="desk-nav">
      <div class="dn-logo"><div class="dn-logo-icon">🗺️</div>Beat Plan Pro</div>
      <div class="dn-links">{btns}</div>
      <div class="dn-right">
        <div><div class="dn-name">{name}</div><div style="font-size:11px;color:#9ca3af;">{rl}</div></div>
        <div class="dn-avatar">{av}</div>
      </div>
    </div>""",unsafe_allow_html=True)

    # Mobile header
    st.markdown(f"""
    <div class="mob-header">
      <div class="mob-logo"><div class="mob-logo-icon">🗺️</div>Beat Plan Pro</div>
      <div style="display:flex;align-items:center;gap:8px;">
        <div style="text-align:right;">
          <div style="font-size:12px;font-weight:600;color:#18181b;">{name}</div>
          <div style="font-size:10px;color:#9ca3af;">{rl}</div>
        </div>
        <div class="mob-av">{av}</div>
      </div>
    </div>""",unsafe_allow_html=True)

    # Mobile bottom nav
    mob="<div class='mob-bot-nav'>"
    for p in nav:
        cls="mbn-item active" if page==p else "mbn-item"
        lbl=p if len(p)<=7 else p[:6]+"…"
        mob+=f'<div class="{cls}"><div class="mbn-icon">{icons.get(p,"")}</div>{lbl}</div>'
    mob+="</div>"
    st.markdown(mob,unsafe_allow_html=True)

    # Invisible functional nav buttons (mobile tap targets)
    st.markdown('<div class="mob-bot-btns">',unsafe_allow_html=True)
    mcols=st.columns(len(nav))
    for i,p in enumerate(nav):
        with mcols[i]:
            if st.button(".",key=f"mb_{p}",use_container_width=True): go(p)
    st.markdown("</div>",unsafe_allow_html=True)

    # Desktop: invisible functional buttons matching top nav
    st.markdown("""
    <style>
    .desk-nav-btns{display:flex;height:0;overflow:hidden;margin:0;padding:0;}
    .desk-nav-btns .stButton>button{opacity:0!important;height:1px!important;min-height:0!important;
      padding:0!important;border:none!important;background:transparent!important;box-shadow:none!important;}
    @media(max-width:768px){.desk-nav-btns{display:none!important;}}
    </style>
    <div class="desk-nav-btns">""",unsafe_allow_html=True)
    dcols=st.columns(len(nav)+2)
    for i,p in enumerate(nav):
        with dcols[i]:
            if st.button(p,key=f"db_{p}",use_container_width=True): go(p)
    st.markdown("</div>",unsafe_allow_html=True)

def tl_item(vd,count,cities,stores,is_today=False):
    bc="tod" if is_today else "fut"
    pills="".join(f"<span class='tl-p'>{s}</span>" for s in stores[:4])
    if len(stores)>4: pills+=f"<span class='tl-p'>+{len(stores)-4}</span>"
    tag="<span class='bdg bp'>Today</span>" if is_today else ""
    st.markdown(f"""
    <div class="tl">
      <div class="tl-date {bc}">
        <div class="tl-day">{vd.strftime('%d')}</div>
        <div class="tl-mon">{vd.strftime('%b')}</div>
      </div>
      <div style="flex:1;min-width:0;">
        <div class="tl-tt">{count} stores · {vd.strftime('%A')}</div>
        <div class="tl-sb">{cities}</div>
        <div class="tl-pl">{pills}</div>
      </div>
      {tag}
    </div>""",unsafe_allow_html=True)


# ── LOGIN ──────────────────────────────────────────────────
if not st.session_state.li:
    st.markdown("<div class='lg-wrap'>",unsafe_allow_html=True)
    st.markdown("""
    <div class="lg-top">
      <div class="lg-ico">🗺️</div>
      <div class="lg-tt">Beat Plan Pro</div>
      <div class="lg-sb">Smart store visit planning for field teams</div>
    </div>""",unsafe_allow_html=True)

    ltype=st.radio("Role",["🛡️  Admin","👷  Employee"],horizontal=True,label_visibility="collapsed")
    st.markdown("<div style='height:10px'></div>",unsafe_allow_html=True)

    if "Admin" in ltype:
        st.markdown("<div class='lg-lbl'>👤 Username</div>",unsafe_allow_html=True)
        user=st.text_input("u",placeholder="Admin username",key="au",label_visibility="collapsed")
        st.markdown("<div class='lg-lbl'>🔒 Password</div>",unsafe_allow_html=True)
        pwd=st.text_input("p",type="password",placeholder="Password",key="ap",label_visibility="collapsed")
        st.markdown("<div style='height:6px'></div>",unsafe_allow_html=True)
        if st.button("Sign in as Admin →",type="primary",use_container_width=True):
            if not user or not pwd: st.error("Enter both fields.")
            else:
                df=st.session_state.adf
                ok=((df["Username"].astype(str).str.strip()==user.strip())&(df["Password"].astype(str).str.strip()==pwd.strip())) if "Username" in df.columns else pd.Series([False])
                if ok.any(): st.session_state.update(li=True,role="admin",en="Admin",pg="Home"); st.rerun()
                else: st.error("❌ Incorrect credentials.")
    else:
        st.markdown("<div class='lg-lbl'>🪪 Employee Code</div>",unsafe_allow_html=True)
        ec_in=st.text_input("ec",placeholder="e.g. EMP001",key="ec_in",label_visibility="collapsed")
        st.markdown("<div class='lg-lbl'>🔒 Password</div>",unsafe_allow_html=True)
        ep=st.text_input("ep",type="password",placeholder="Password",key="ep_in",label_visibility="collapsed")
        st.markdown("<div style='height:6px'></div>",unsafe_allow_html=True)
        if st.button("Sign in →",type="primary",use_container_width=True):
            if not ec_in or not ep: st.error("Enter both fields.")
            else:
                df=st.session_state.edf
                m=df[(df["EmployeeCode"].astype(str).str.strip()==ec_in.strip())&(df["Password"].astype(str).str.strip()==ep.strip())] if "EmployeeCode" in df.columns else pd.DataFrame()
                if not m.empty:
                    st.session_state.update(li=True,role="employee",ec=str(m.iloc[0]["EmployeeCode"]),en=m.iloc[0]["EmployeeName"],pg="Home"); st.rerun()
                else: st.error("❌ Incorrect credentials.")

    st.markdown("</div>",unsafe_allow_html=True)
    st.stop()

# ── App shell ─────────────────────────────────────────────
role=st.session_state.role; emp_code=st.session_state.ec
emp_name=st.session_state.en; page=st.session_state.pg

render_shell(emp_name,role,page)
st.markdown("<div class='page-pad'>",unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  ADMIN PAGES
# ══════════════════════════════════════════════════════════
if role=="admin":
    tp=int((st.session_state.pdf["VisitDate"]==date.today()).sum()) if "VisitDate" in st.session_state.pdf.columns else 0

    if page=="Home":
        st.markdown(f"""
        <div class="greeting">
          <div class="g-hi">Admin Dashboard 📊</div>
          <div class="g-sub">Full overview of all field activity</div>
          <div class="g-date">{date.today().strftime('%A, %d %B %Y')}</div>
        </div>""",unsafe_allow_html=True)

        stat_cards([
            ("linear-gradient(90deg,#4f46e5,#7c3aed)","👥",len(st.session_state.edf),"Employees","Active team","#4f46e5"),
            ("linear-gradient(90deg,#06b6d4,#0284c7)","🏪",len(st.session_state.gdf),"Stores","Total stores","#0891b2"),
            ("linear-gradient(90deg,#f59e0b,#d97706)","📋",len(st.session_state.pdf),"All Plans","Total visits","#d97706"),
            ("linear-gradient(90deg,#10b981,#059669)","📍",tp,"Today","Visits today","#059669"),
        ])

        c1,c2=st.columns([3,2])
        with c1:
            st.markdown("<div class='sec-hd'>📋 Recent Plans</div>",unsafe_allow_html=True)
            if not st.session_state.pdf.empty:
                ds=st.session_state.pdf.sort_values("VisitDate",ascending=False) if "VisitDate" in st.session_state.pdf.columns else st.session_state.pdf
                st.dataframe(ds.head(10),use_container_width=True,hide_index=True)
            else: empty("📋","No plans yet","Plans appear once employees start planning.")
        with c2:
            st.markdown("<div class='sec-hd'>👥 Team</div>",unsafe_allow_html=True)
            disp=st.session_state.edf.drop(columns=["Password"],errors="ignore")
            if not disp.empty: st.dataframe(disp,use_container_width=True,hide_index=True)
            else: empty("👥","No employees","Add employees to get started.")

        st.markdown("<div style='height:10px'></div>",unsafe_allow_html=True)
        if st.button("🚪  Sign Out",use_container_width=True,key="so_a"):
            for k,v in DEF.items(): st.session_state[k]=v
            st.rerun()

    elif page=="Employees":
        phdr("👥 Employees","Manage your field team members")
        t1,t2,t3=st.tabs(["  View All  ","  Add  ","  Remove  "])

        with t1:
            disp=st.session_state.edf.drop(columns=["Password"],errors="ignore")
            if not disp.empty:
                st.caption(f"{len(disp)} employees in system")
                st.dataframe(disp,use_container_width=True,hide_index=True)
            else: empty("👥","No employees yet","Use Add tab to add team members.")

        with t2:
            ib("Employee code must be unique. They'll use code + password to log in.")
            with st.form("ae",clear_on_submit=True):
                c1,c2=st.columns(2)
                with c1:
                    ec2=st.text_input("Employee Code *",placeholder="e.g. EMP042")
                    en2=st.text_input("Full Name *",placeholder="e.g. Ramesh Kumar")
                with c2:
                    ep2=st.text_input("Password *",type="password",placeholder="Set a password")
                    st.markdown("<div style='height:27px'></div>",unsafe_allow_html=True)
                if st.form_submit_button("➕  Add Employee",type="primary",use_container_width=True):
                    if not ec2 or not en2 or not ep2: st.error("All fields required.")
                    elif sc(st.session_state.edf,"EmployeeCode").astype(str).str.upper().eq(ec2.strip().upper()).any(): st.error(f"Code '{ec2.upper()}' exists.")
                    else:
                        nr=pd.DataFrame([{"EmployeeCode":ec2.strip().upper(),"EmployeeName":en2.strip().title(),"Password":ep2.strip()}])
                        st.session_state.edf=pd.concat([st.session_state.edf,nr],ignore_index=True)
                        if save_sb("employee_master",st.session_state.edf): st.success(f"✅ {en2.strip().title()} added!"); st.rerun()

        with t3:
            if st.session_state.edf.empty: empty("👥","No employees to remove","")
            else:
                wb("Removing an employee is permanent.")
                ed=st.selectbox("Select employee",sc(st.session_state.edf,"EmployeeCode").unique())
                row=st.session_state.edf[sc(st.session_state.edf,"EmployeeCode")==ed]
                nm=sc(row,"EmployeeName").iloc[0] if not row.empty else ed
                st.markdown(f"<div class='si'><div class='si-av av-r'>👤</div><div><div class='si-nm'>{nm}</div><div class='si-mt'>{ed}</div></div></div>",unsafe_allow_html=True)
                if st.button("🗑  Confirm Remove",type="primary",use_container_width=True,key="de"):
                    st.session_state.edf=st.session_state.edf[sc(st.session_state.edf,"EmployeeCode")!=ed]
                    if save_sb("employee_master",st.session_state.edf): st.success(f"✅ {nm} removed."); st.rerun()

    elif page=="Stores":
        phdr("🏪 Stores","Manage your store master list")
        t1,t2,t3=st.tabs(["  View All  ","  Add  ","  Remove  "])

        with t1:
            if not st.session_state.gdf.empty:
                cities=["All"]+sorted(sc(st.session_state.gdf,"City").dropna().unique().tolist())
                cf=st.selectbox("Filter by city",cities)
                ds=st.session_state.gdf if cf=="All" else st.session_state.gdf[sc(st.session_state.gdf,"City")==cf]
                st.caption(f"{len(ds)} stores")
                st.dataframe(ds,use_container_width=True,hide_index=True)
            else: empty("🏪","No stores yet","Use Add tab to add stores.")

        with t2:
            ib("GSTIN format: <b>22AAAAA0000A1Z5</b> (15 chars)")
            with st.form("as2",clear_on_submit=True):
                c1,c2=st.columns(2)
                with c1:
                    sn=st.text_input("Store Name *",placeholder="e.g. Reliance Fresh")
                    gs=st.text_input("GST Number *",max_chars=15,placeholder="22AAAAA0000A1Z5")
                with c2:
                    cy=st.text_input("City *",placeholder="e.g. Lucknow")
                    eo=sc(st.session_state.edf,"EmployeeCode").unique().tolist() or ["—"]
                    es=st.selectbox("Assign to Employee *",eo)
                if st.form_submit_button("➕  Add Store",type="primary",use_container_width=True):
                    g=gs.strip().upper()
                    if not sn or not g or not cy: st.error("All fields required.")
                    elif not gstin_ok(g): st.error("Invalid GSTIN. Example: 22AAAAA0000A1Z5")
                    elif sc(st.session_state.gdf,"GSTNumber").astype(str).str.upper().eq(g).any(): st.error(f"GST '{g}' exists.")
                    else:
                        nid=f"S{len(st.session_state.gdf)+1:05d}"
                        ns=pd.DataFrame([{"StoreID":nid,"StoreName":sn.strip().title(),"GSTNumber":g,"City":cy.strip().title(),"EmployeeCode":es}])
                        st.session_state.gdf=pd.concat([st.session_state.gdf,ns],ignore_index=True)
                        if save_sb("gst_master",st.session_state.gdf): st.success(f"✅ {sn.strip().title()} added!"); st.rerun()

        with t3:
            if st.session_state.gdf.empty: empty("🏪","No stores to remove","")
            else:
                wb("Removing a store is permanent.")
                sd=st.selectbox("Select store",sc(st.session_state.gdf,"StoreID").unique())
                row=st.session_state.gdf[sc(st.session_state.gdf,"StoreID")==sd]
                snm=sc(row,"StoreName").iloc[0] if not row.empty else sd
                st.markdown(f"<div class='si'><div class='si-av av-r'>🏪</div><div><div class='si-nm'>{snm}</div><div class='si-mt'>{sd}</div></div></div>",unsafe_allow_html=True)
                if st.button("🗑  Confirm Remove",type="primary",use_container_width=True,key="ds"):
                    st.session_state.gdf=st.session_state.gdf[sc(st.session_state.gdf,"StoreID")!=sd]
                    if save_sb("gst_master",st.session_state.gdf): st.success(f"✅ {snm} removed."); st.rerun()

    elif page=="View Plans":
        phdr("📋 View Plans","Browse and filter all employee beat plans")
        with st.expander("🔍 Filters",expanded=True):
            c1,c2,c3=st.columns(3)
            with c1: fe=st.selectbox("Employee",["All"]+list(sc(st.session_state.pdf,"EmployeeName").dropna().unique()))
            with c2: fc=st.selectbox("City",["All"]+list(sc(st.session_state.pdf,"City").dropna().unique()))
            with c3: dr=st.date_input("Date Range",value=(date.today()-timedelta(days=30),date.today()))

        fp=st.session_state.pdf.copy()
        if fe!="All" and "EmployeeName" in fp.columns: fp=fp[fp["EmployeeName"]==fe]
        if fc!="All" and "City" in fp.columns: fp=fp[fp["City"]==fc]
        if isinstance(dr,(list,tuple)) and len(dr)==2 and "VisitDate" in fp.columns:
            fp=fp[(fp["VisitDate"]>=dr[0])&(fp["VisitDate"]<=dr[1])]

        c1,c2,c3,c4=st.columns(4)
        c1.metric("Plans",len(fp)); c2.metric("Employees",sc(fp,"EmployeeName").nunique())
        c3.metric("Cities",sc(fp,"City").nunique()); c4.metric("Stores",sc(fp,"Store").nunique())
        st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
        if not fp.empty:
            st.dataframe(fp.sort_values("VisitDate",ascending=False) if "VisitDate" in fp.columns else fp,use_container_width=True,hide_index=True)
            dl_btn(fp,"adl","Beat_Plan_Admin")
        else: empty("📋","No matching plans","Adjust the filters above.")

    elif page=="Refresh":
        phdr("🔄 Sync Data","Pull latest records from Supabase")
        ib("Refreshes all tables: Employees, Stores, Plans and Admin.")
        c1,_=st.columns([1,2])
        with c1:
            if st.button("🔄  Refresh Now",type="primary",use_container_width=True):
                with st.spinner("Syncing…"):
                    st.session_state.edf=load_sb("employee_master",EC)
                    st.session_state.gdf=load_sb("gst_master",GC)
                    st.session_state.pdf=load_sb("planned_visits",PC)
                    st.session_state.adf=load_sb("admin_master",AC)
                st.success("✅ All data refreshed!"); st.rerun()


# ══════════════════════════════════════════════════════════
#  EMPLOYEE PAGES
# ══════════════════════════════════════════════════════════
else:
    my_stores=st.session_state.gdf[sc(st.session_state.gdf,"EmployeeCode").astype(str)==str(emp_code)] if not st.session_state.gdf.empty else pd.DataFrame(columns=GC)
    my_plans=st.session_state.pdf[sc(st.session_state.pdf,"EmployeeCode").astype(str)==str(emp_code)]

    if page=="Home":
        hour=dt_mod.datetime.now().hour
        greet="Good morning" if hour<12 else "Good afternoon" if hour<17 else "Good evening"
        first=emp_name.split()[0]

        st.markdown(f"""
        <div class="greeting">
          <div class="g-hi">{greet}, {first}! 👋</div>
          <div class="g-sub">Ready to plan your store visits?</div>
          <div class="g-date">{date.today().strftime('%A, %d %B %Y')}</div>
        </div>""",unsafe_allow_html=True)

        tp2=my_plans[my_plans["VisitDate"]==date.today()] if "VisitDate" in my_plans.columns else pd.DataFrame()
        tm=my_plans[pd.to_datetime(sc(my_plans,"VisitDate"),errors="coerce").dt.month==date.today().month] if "VisitDate" in my_plans.columns else pd.DataFrame()

        stat_cards([
            ("linear-gradient(90deg,#4f46e5,#7c3aed)","🏪",len(my_stores),"My Stores",f"{sc(my_stores,'City').nunique()} cities","#4f46e5"),
            ("linear-gradient(90deg,#10b981,#059669)","📍",len(tp2),"Today","Max 10/day","#059669"),
            ("linear-gradient(90deg,#f59e0b,#d97706)","📅",len(tm),"This Month",date.today().strftime("%b %Y"),"#d97706"),
            ("linear-gradient(90deg,#06b6d4,#0284c7)","📋",len(my_plans),"All Plans","All time","#0891b2"),
        ])

        # Quick actions
        st.markdown("<div class='sec-hd'>Quick Actions</div>",unsafe_allow_html=True)
        st.markdown("""
        <div class="qa-row">
          <div class="qa-card"><div class="qa-ico" style="background:#eef2ff;">🎯</div><div class="qa-lbl">New Beat Plan</div><div class="qa-dsc">Plan today's visits</div></div>
          <div class="qa-card"><div class="qa-ico" style="background:#f0fdf4;">📅</div><div class="qa-lbl">My Plans</div><div class="qa-dsc">All scheduled visits</div></div>
          <div class="qa-card"><div class="qa-ico" style="background:#fffbeb;">➕</div><div class="qa-lbl">Add Store</div><div class="qa-dsc">Request new store</div></div>
        </div>""",unsafe_allow_html=True)
        qa1,qa2,qa3=st.columns(3)
        with qa1:
            if st.button("🎯  New Beat Plan",use_container_width=True,key="qa1"): go("Beat Plan")
        with qa2:
            if st.button("📅  My Plans",use_container_width=True,key="qa2"): go("My Plans")
        with qa3:
            if st.button("➕  Add Store",use_container_width=True,key="qa3"): go("Add Store")

        st.markdown("<div style='height:6px'></div>",unsafe_allow_html=True)

        cl,cr=st.columns(2)
        with cl:
            pn=len(tp2); col=pc_color(pn); pct=min(pn*10,100)
            st.markdown("<div class='sec-hd'>📍 Today's Plan</div>",unsafe_allow_html=True)
            st.markdown(f"""
            <div class="card">
              <div class="prog-row">
                <span class="prog-lbl">Progress</span>
                <span class="prog-num" style="color:{col};">{pn}/10</span>
              </div>
              <div class="prog-track"><div class="prog-fill" style="width:{pct}%;background:{col};"></div></div>
              <div class="prog-hint">{"🚫 Daily limit reached" if pn>=10 else f"✅ {10-pn} more store(s) available"}</div>
            </div>""",unsafe_allow_html=True)
            if not tp2.empty:
                for _,row in tp2.iterrows():
                    st.markdown(f"""
                    <div class="si">
                      <div class="si-av av-g">✓</div>
                      <div style="flex:1;min-width:0;"><div class="si-nm">{row.get('Store','—')}</div><div class="si-mt">{row.get('City','—')}</div></div>
                      <span class="bdg bg">Planned</span>
                    </div>""",unsafe_allow_html=True)
            else: empty("📍","Nothing planned today","Tap New Beat Plan to start.")

        with cr:
            st.markdown("<div class='sec-hd'>📆 Upcoming</div>",unsafe_allow_html=True)
            if "VisitDate" in st.session_state.pdf.columns:
                up=st.session_state.pdf[(sc(st.session_state.pdf,"EmployeeCode").astype(str)==str(emp_code))&(st.session_state.pdf["VisitDate"]>date.today())].sort_values("VisitDate")
                if up.empty: empty("📆","No upcoming visits","Plan visits in Beat Plan.")
                else:
                    for vd in sorted(up["VisitDate"].unique())[:4]:
                        pl=up[up["VisitDate"]==vd]
                        cities=", ".join(sorted(sc(pl,"City").dropna().unique().tolist()))
                        stores=sc(pl,"Store").dropna().unique().tolist()
                        tl_item(vd,len(pl),cities,stores,False)

        st.markdown("<div style='height:10px'></div>",unsafe_allow_html=True)
        if st.button("🚪  Sign Out",use_container_width=True,key="so_e"):
            for k,v in DEF.items(): st.session_state[k]=v
            st.rerun()

    elif page=="Beat Plan":
        phdr("🎯 Beat Plan","Add stores to your daily visit list")
        if my_stores.empty:
            empty("⚠️","No stores assigned","Contact your admin to assign stores.")
            st.stop()

        c1,c2,c3=st.columns([1,2,1])
        with c1: vd=st.date_input("📅 Visit Date",value=date.today(),key="bd",min_value=date.today()-timedelta(days=7))
        with c2:
            co=sorted(sc(my_stores,"City").dropna().unique().tolist())
            sc2=st.multiselect(f"🌍 Filter Cities (max 3)",co,max_selections=3,key="cms")
        with c3:
            st.markdown("<div style='height:27px'></div>",unsafe_allow_html=True)
            if st.button("🔍  Apply",use_container_width=True): st.session_state.sc=sc2; st.rerun()

        daily=my_plans[my_plans["VisitDate"]==vd] if "VisitDate" in my_plans.columns else pd.DataFrame(columns=PC)
        pn=len(daily); col=pc_color(pn); pct=min(pn*10,100)

        st.markdown(f"""
        <div class="card">
          <div class="card-hdr">
            <div class="card-hdr-ico" style="background:#eef2ff;">📊</div>
            {vd.strftime('%d %b %Y')} — Progress
            <span class="card-pill" style="background:{'#fef2f2' if pn>=10 else '#eef2ff'};color:{'#b91c1c' if pn>=10 else '#4338ca'};">{pn}/10</span>
          </div>
          <div class="prog-row">
            <span class="prog-lbl">{"🚫 Limit reached" if pn>=10 else f"✅ {10-pn} more available"}</span>
            <span class="prog-num" style="color:{col};">{pct}%</span>
          </div>
          <div class="prog-track"><div class="prog-fill" style="width:{pct}%;background:{col};"></div></div>
        </div>""",unsafe_allow_html=True)

        if not daily.empty:
            with st.expander(f"✅ Already planned ({pn} stores)"):
                cols=[c for c in ["Store","City","GSTNumber","StoreID"] if c in daily.columns]
                st.dataframe(daily[cols],use_container_width=True,hide_index=True)

        if pn<10:
            show_c=st.session_state.sc or sc(my_stores,"City").unique().tolist()
            avail=my_stores[sc(my_stores,"City").isin(show_c)&~sc(my_stores,"StoreID").isin(sc(daily,"StoreID").tolist())]
            st.markdown(f"<div class='sec-hd'>🏪 Available Stores <span class='sec-ct'>{len(avail)}</span></div>",unsafe_allow_html=True)
            if avail.empty: empty("🎉","All done!","All stores planned for selected cities.")
            else:
                for idx,row in avail.iterrows():
                    c1,c2=st.columns([6,1])
                    with c1:
                        st.markdown(f"""
                        <div class="si">
                          <div class="si-av av-i">🏪</div>
                          <div style="flex:1;min-width:0;"><div class="si-nm">{row.get('StoreName','—')}</div><div class="si-mt">{row.get('City','—')} · {row.get('GSTNumber','—')}</div></div>
                          <span class="bdg bg">Available</span>
                        </div>""",unsafe_allow_html=True)
                    with c2:
                        st.markdown("<div style='height:14px'></div>",unsafe_allow_html=True)
                        if st.button("➕",key=f"a_{idx}_{vd}",use_container_width=True):
                            nr=pd.DataFrame([{"EmployeeCode":emp_code,"EmployeeName":emp_name,"City":row.get("City",""),"Store":row.get("StoreName",""),"StoreID":row.get("StoreID",""),"GSTNumber":row.get("GSTNumber",""),"VisitDate":vd}])
                            st.session_state.pdf=pd.concat([st.session_state.pdf,nr],ignore_index=True)
                            if save_sb("planned_visits",st.session_state.pdf): st.success(f"✅ {row.get('StoreName','')} added!"); st.rerun()

        st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
        dl_btn(my_plans,"edl",f"Beat_Plan_{emp_code}")

    elif page=="My Plans":
        phdr("📅 My Plans","All your scheduled store visits")
        if my_plans.empty: empty("📅","No plans yet","Go to Beat Plan to schedule visits.")
        else:
            tm2=my_plans[pd.to_datetime(sc(my_plans,"VisitDate"),errors="coerce").dt.month==date.today().month] if "VisitDate" in my_plans.columns else pd.DataFrame()
            stat_cards([
                ("linear-gradient(90deg,#4f46e5,#7c3aed)","📋",len(my_plans),"Total Plans","All time","#4f46e5"),
                ("linear-gradient(90deg,#10b981,#059669)","📅",len(tm2),"This Month",date.today().strftime("%b"),"#059669"),
                ("linear-gradient(90deg,#06b6d4,#0284c7)","🌍",sc(my_plans,"City").nunique(),"Cities","Covered","#0891b2"),
                ("linear-gradient(90deg,#f59e0b,#d97706)","🏪",sc(my_plans,"Store").nunique(),"Stores","Unique","#d97706"),
            ])
            with st.expander("🔍 Filter",expanded=False):
                fc2=st.selectbox("City",["All"]+sorted(sc(my_plans,"City").dropna().unique().tolist()),key="mp_c")
                fd=st.date_input("From date",value=date.today()-timedelta(days=30),key="mpd")
            df_mp=my_plans.copy()
            if fc2!="All" and "City" in df_mp.columns: df_mp=df_mp[df_mp["City"]==fc2]
            if "VisitDate" in df_mp.columns: df_mp=df_mp[df_mp["VisitDate"]>=fd]
            st.dataframe(df_mp.sort_values("VisitDate",ascending=False) if "VisitDate" in df_mp.columns else df_mp,use_container_width=True,hide_index=True)
            dl_btn(df_mp,"mdl",f"My_Plans_{emp_code}")

    elif page=="Upcoming":
        phdr("📆 Upcoming","Your planned visits from today onwards")
        if "VisitDate" not in st.session_state.pdf.columns: empty("📆","No upcoming visits","Plan visits in Beat Plan.")
        else:
            up2=st.session_state.pdf[(sc(st.session_state.pdf,"EmployeeCode").astype(str)==str(emp_code))&(st.session_state.pdf["VisitDate"]>=date.today())].sort_values("VisitDate")
            if up2.empty: empty("📆","No upcoming visits","Plan visits in Beat Plan.")
            else:
                st.markdown(f'<div class="ib">📅  <b>{len(up2)} visits</b> across <b>{len(up2["VisitDate"].unique())} days</b></div>',unsafe_allow_html=True)
                for vd in sorted(up2["VisitDate"].unique()):
                    pl=up2[up2["VisitDate"]==vd]
                    cities=", ".join(sorted(sc(pl,"City").dropna().unique().tolist()))
                    stores=sc(pl,"Store").dropna().unique().tolist()
                    tl_item(vd,len(pl),cities,stores,vd==date.today())

    elif page=="Analytics":
        phdr("📈 Analytics","Your personal performance insights")
        if my_plans.empty: empty("📈","No data yet","Analytics appear once you plan visits.")
        else:
            tm3=my_plans[pd.to_datetime(sc(my_plans,"VisitDate"),errors="coerce").dt.month==date.today().month] if "VisitDate" in my_plans.columns else pd.DataFrame()
            stat_cards([
                ("linear-gradient(90deg,#4f46e5,#7c3aed)","📋",len(my_plans),"Total Visits","All time","#4f46e5"),
                ("linear-gradient(90deg,#10b981,#059669)","📅",len(tm3),"This Month",date.today().strftime("%b"),"#059669"),
                ("linear-gradient(90deg,#06b6d4,#0284c7)","🌍",sc(my_plans,"City").nunique(),"Cities","Covered","#0891b2"),
                ("linear-gradient(90deg,#f59e0b,#d97706)","🏪",sc(my_plans,"Store").nunique(),"Stores","Unique","#d97706"),
            ])
            c1,c2=st.columns(2)
            with c1:
                st.markdown("<div class='sec-hd'>Visits by City</div>",unsafe_allow_html=True)
                if "City" in my_plans.columns: st.bar_chart(my_plans.groupby("City").size(),color="#4f46e5")
            with c2:
                st.markdown("<div class='sec-hd'>Monthly Trend</div>",unsafe_allow_html=True)
                if "VisitDate" in my_plans.columns:
                    tmp=my_plans.copy()
                    tmp["Month"]=pd.to_datetime(tmp["VisitDate"],errors="coerce").dt.to_period("M").astype(str)
                    st.line_chart(tmp.groupby("Month").size(),color="#06b6d4")
            st.markdown("<div class='sec-hd'>Top Stores <span class='sec-ct'>Top 10</span></div>",unsafe_allow_html=True)
            if "Store" in my_plans.columns:
                top=my_plans.groupby("Store").agg(Visits=("Store","count"),City=("City","first")).reset_index().sort_values("Visits",ascending=False).head(10)
                st.dataframe(top,use_container_width=True,hide_index=True)

    elif page=="Add Store":
        phdr("➕ Add Store","Request a store for your territory")
        ib("GSTIN format: <b>22AAAAA0000A1Z5</b> (15 characters)")
        with st.form("sr",clear_on_submit=True):
            c1,c2=st.columns(2)
            with c1:
                sn2=st.text_input("Store Name *",placeholder="e.g. Reliance Fresh")
                cy2=st.text_input("City *",placeholder="e.g. Lucknow")
            with c2:
                gs2=st.text_input("GST Number *",max_chars=15,placeholder="22AAAAA0000A1Z5")
                st.text_area("Remarks (optional)",height=82,placeholder="Notes for admin…")
            if st.form_submit_button("➕  Add to My Territory",type="primary",use_container_width=True):
                g2=gs2.strip().upper()
                if not sn2 or not cy2 or not g2: st.error("All fields required.")
                elif not gstin_ok(g2): st.error("Invalid GSTIN. Format: 22AAAAA0000A1Z5")
                elif sc(st.session_state.gdf,"GSTNumber").astype(str).str.upper().eq(g2).any(): st.error(f"GSTIN '{g2}' exists.")
                else:
                    nid=f"S{len(st.session_state.gdf)+1:05d}"
                    ns=pd.DataFrame([{"StoreID":nid,"StoreName":sn2.strip().title(),"GSTNumber":g2,"City":cy2.strip().title(),"EmployeeCode":emp_code}])
                    st.session_state.gdf=pd.concat([st.session_state.gdf,ns],ignore_index=True)
                    if save_sb("gst_master",st.session_state.gdf): st.success(f"✅ {sn2.strip().title()} added!"); st.rerun()

# ── Close page wrapper & footer ───────────────────────────
st.markdown("</div>",unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center;font-size:12px;color:#c4c9d9;padding:20px 0 80px;'>
  Beat Plan Pro · 2026 · Built by Bipin Pandey
</div>""",unsafe_allow_html=True)
