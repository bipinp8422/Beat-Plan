import streamlit as st
import pandas as pd
import bridge

st.set_page_config(page_title="Beat Plan + TPS", page_icon="🚀", layout="wide",
                   initial_sidebar_state="expanded")

DEFAULTS = {"logged_in": False, "role": "", "user_type": None, "user_id": "", "user_name": "",
            "emp_code": "", "emp_name": "", "selected_cities": []}
for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)


def _set_session(role, uid, name):
    """One session, both apps' keys (Beat uses role/emp_code/emp_name, TPS uses user_type/user_id/user_name)."""
    st.session_state.update(logged_in=True, role=role, user_type=role, user_id=uid, user_name=name,
                            emp_code=uid, emp_name=name)


def _first(db, table, **eq):
    q = db.table(table).select("*")
    for c, v in eq.items():
        q = q.eq(c, v)
    d = q.execute().data
    return d[0] if d else None


def _beat_row(table, user_col, user, pwd):
    df = bridge.fetch_all(bridge.beat_db(), table)
    if df.empty:
        return None
    df.columns = [c.lower() for c in df.columns]
    m = df[(df[user_col].astype(str).str.strip() == user.strip()) &
           (df["password"].astype(str).str.strip() == pwd.strip())]
    return m.iloc[0].to_dict() if not m.empty else None


def login():
    st.title("🚀 Beat Plan + TPS — Login")
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        role = st.radio("Login as", ["Employee", "Team Lead", "Admin"], horizontal=True)
        uid = st.text_input("ID / Code")
        pwd = st.text_input("Password", type="password")
        if st.button("🔓 Login", type="primary", use_container_width=True):
            try:
                if role == "Employee":
                    r = _first(bridge.tps_db(), "employee_users", emp_id=uid, emp_password=pwd)
                    if r:
                        e = _first(bridge.tps_db(), "employees", emp_id=uid)
                        _set_session("employee", uid, (e or {}).get("emp_name", uid))
                    else:
                        b = _beat_row("employee_master", "employeecode", uid, pwd)
                        if not b:
                            return st.error("❌ Invalid credentials.")
                        _set_session("employee", uid, b.get("employeename", uid))
                elif role == "Team Lead":
                    r = _first(bridge.tps_db(), "tl_users", tl_id=uid, tl_password=pwd)
                    if not r:
                        return st.error("❌ Invalid credentials.")
                    _set_session("tl", uid, r["tl_name"])
                else:
                    r = _first(bridge.tps_db(), "admin_users", admin_id=uid, admin_password=pwd)
                    if r:
                        _set_session("admin", uid, r["admin_name"])
                    elif _beat_row("admin_master", "username", uid, pwd):
                        _set_session("admin", uid, uid)
                    else:
                        return st.error("❌ Invalid credentials.")
                st.rerun()
            except Exception as ex:
                st.error(f"Login error: {ex}")


def home():
    st.title(f"🏠 Welcome, {st.session_state.user_name}")
    role, uid = st.session_state.role, st.session_state.user_id
    miss_store, miss_counter, stores, counters = bridge.compare()

    if role == "employee":
        stores = stores[stores["EmployeeCode"] == uid]
        counters = counters[counters["emp_id"] == uid]
        miss_store = miss_store[miss_store["emp_id"] == uid]
        miss_counter = miss_counter[miss_counter["EmployeeCode"] == uid]

    c = st.columns(4)
    c[0].metric("TPS Counters", len(counters))
    c[1].metric("Beat Plan Stores", len(stores))
    c[2].metric("Counters missing in Beat Plan", len(miss_store))
    c[3].metric("Stores missing in TPS", len(miss_counter))

    if role == "employee":
        planned = bridge.fetch_all(bridge.beat_db(), "planned_visits")
        if not planned.empty:
            planned.columns = [c_.lower() for c_ in planned.columns]
            ids = set(planned[planned["employeecode"].astype(str) == uid]["storeid"].astype(str))
            never = stores[~stores["StoreID"].astype(str).isin(ids)]
            st.info(f"📦 {len(never)} of your counters have never been in a beat plan. "
                    f"Open **Beat Plan → Pending Stores**.")

    if miss_store.empty and miss_counter.empty:
        st.success("✅ TPS counters and Beat Plan stores are fully in sync.")
        return
    if not miss_store.empty:
        with st.expander(f"Counters in TPS but not in Beat Plan ({len(miss_store)})"):
            st.dataframe(miss_store[["emp_id", "partner_name", "gst_number", "city"]],
                         use_container_width=True, hide_index=True)
    if not miss_counter.empty:
        with st.expander(f"Stores in Beat Plan but not in TPS ({len(miss_counter)}) — add via TPS request"):
            st.dataframe(miss_counter[["EmployeeCode", "StoreName", "GSTNumber", "City"]],
                         use_container_width=True, hide_index=True)
    if role == "admin" and not miss_store.empty:
        if st.button("🔄 Create all missing Beat Plan stores from TPS counters", type="primary"):
            n = bridge.sync_all_missing()
            for k in ("gst_df",):
                st.session_state.pop(k, None)  # force Beat Plan page to reload stores
            st.success(f"✅ {n} store(s) created.")
            st.rerun()


if not st.session_state.logged_in:
    login()
    st.stop()

from pathlib import Path
HERE = Path(__file__).parent

# Auto-build the page files from your ORIGINAL scripts (beat_original.py / tps_original.py) if present.
try:
    import make_pages
    for _src, _dst, _fn in (("beat_original.py", "beat_plan.py", make_pages.make_beat),
                            ("tps_original.py", "tps.py", make_pages.make_tps)):
        if (HERE / _src).exists() and not (HERE / _dst).exists():
            (HERE / _dst).write_text(_fn((HERE / _src).read_text(encoding="utf-8")), encoding="utf-8")
except Exception as _e:
    st.error(f"Could not build page files from the original scripts: {_e}")


def _page(fname, title, icon):
    if (HERE / fname).exists():
        return st.Page(str(HERE / fname), title=title, icon=icon)

    def _missing():
        st.error(f"❌ `{fname}` was not found next to app.py. Run make_pages.py, "
                 f"then commit and push {fname} to the repo root.")
        st.caption("Files found here: " + ", ".join(sorted(p.name for p in HERE.iterdir())))
    return st.Page(_missing, title=title + " (missing)", icon="⚠️", url_path=Path(fname).stem)


pages = [st.Page(home, title="Home", icon="🏠", default=True)]
if st.session_state.role in ("admin", "employee"):
    pages.append(_page("beat_plan.py", "Beat Plan", "🚀"))
pages.append(_page("tps.py", "TPS Counters", "📊"))

with st.sidebar:
    st.caption(f"👤 {st.session_state.user_name} ({st.session_state.role})")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()

st.navigation(pages).run()
