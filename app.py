
# FULL UPDATED APP
# Changes:
# 1. Multiple stores can be planned on same day.
# 2. Same store cannot be planned twice on same day.
# 3. Pending Stores table added.
# 4. Dropdown only shows stores not yet planned for selected date.
# 5. All original features preserved.

import streamlit as st
import pandas as pd
import os
import re
from datetime import date

st.set_page_config(page_title="Beat Plan Management", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EMPLOYEE_FILE = os.path.join(BASE_DIR, "Employee_Master.xlsx")
GST_FILE = os.path.join(BASE_DIR, "GST_Master.xlsx")
PLANNED_FILE = os.path.join(BASE_DIR, "Planned_Visits.xlsx")
ADMIN_FILE = os.path.join(BASE_DIR, "Admin_Master.xlsx")

if not os.path.exists(EMPLOYEE_FILE):
    pd.DataFrame(columns=["EmployeeCode","EmployeeName","Password"]).to_excel(EMPLOYEE_FILE,index=False)

if not os.path.exists(GST_FILE):
    pd.DataFrame(columns=["StoreID","StoreName","GSTNumber","City","EmployeeCode"]).to_excel(GST_FILE,index=False)

if not os.path.exists(PLANNED_FILE):
    pd.DataFrame(columns=["EmployeeCode","EmployeeName","City","Store","StoreID","VisitDate","Planned"]).to_excel(PLANNED_FILE,index=False)

if not os.path.exists(ADMIN_FILE):
    pd.DataFrame([{"Username":"admin","Password":"admin123"}]).to_excel(ADMIN_FILE,index=False)

employee_df = pd.read_excel(EMPLOYEE_FILE)
gst_df = pd.read_excel(GST_FILE)
planned_df = pd.read_excel(PLANNED_FILE)
admin_df = pd.read_excel(ADMIN_FILE)

if "VisitDate" in planned_df.columns:
    planned_df["VisitDate"] = pd.to_datetime(planned_df["VisitDate"], errors="coerce")

for k,v in {"logged_in":False,"role":"","emp_code":"","emp_name":""}.items():
    if k not in st.session_state:
        st.session_state[k]=v

def validate_gst(gst):
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][A-Z0-9]Z[A-Z0-9]$'
    return bool(re.match(pattern, gst.upper()))

if not st.session_state.logged_in:

    st.title("Beat Plan Management System")

    login_type = st.radio("Login Type",["Admin","Employee"])

    if login_type=="Admin":

        user = st.text_input("Username")
        pwd = st.text_input("Password",type="password")

        if st.button("Admin Login"):

            x = admin_df[
                (admin_df["Username"].astype(str)==user) &
                (admin_df["Password"].astype(str)==pwd)
            ]

            if x.empty:
                st.error("Invalid Admin Credentials")
            else:
                st.session_state.logged_in=True
                st.session_state.role="admin"
                st.rerun()

    else:

        emp_code = st.text_input("Employee Code")
        pwd = st.text_input("Password",type="password")

        if st.button("Employee Login"):

            x = employee_df[
                (employee_df["EmployeeCode"].astype(str)==emp_code) &
                (employee_df["Password"].astype(str)==pwd)
            ]

            if x.empty:
                st.error("Invalid Employee Credentials")
            else:
                st.session_state.logged_in=True
                st.session_state.role="employee"
                st.session_state.emp_code=x.iloc[0]["EmployeeCode"]
                st.session_state.emp_name=x.iloc[0]["EmployeeName"]
                st.rerun()

    st.stop()

if st.sidebar.button("Logout"):
    for k in ["logged_in","role","emp_code","emp_name"]:
        st.session_state[k] = False if k=="logged_in" else ""
    st.rerun()

if st.session_state.role=="admin":

    st.sidebar.title("Admin Panel")

    menu = st.sidebar.radio(
        "Menu",
        [
            "Dashboard",
            "Upload Employee Master",
            "Upload GST Master",
            "Create Employee",
            "All Employees",
            "All Stores",
            "All Visit Plans"
        ]
    )

    if menu=="Dashboard":

        st.title("Admin Dashboard")
        st.metric("Total Employees", len(employee_df))
        st.metric("Total Stores", len(gst_df))
        st.metric("Total Visits", len(planned_df))

    elif menu=="Upload Employee Master":

        st.title("Upload Employee Master")
        file = st.file_uploader("Upload Excel",type=["xlsx"])

        if file:
            df = pd.read_excel(file)
            df.to_excel(EMPLOYEE_FILE,index=False)
            st.success("Employee Master Uploaded")

    elif menu=="Upload GST Master":

        st.title("Upload GST Master")
        file = st.file_uploader("Upload Excel",type=["xlsx"])

        if file:
            df = pd.read_excel(file)
            df.to_excel(GST_FILE,index=False)
            st.success("GST Master Uploaded")

    elif menu=="Create Employee":

        st.title("Create Employee")

        emp_code = st.text_input("Employee Code")
        emp_name = st.text_input("Employee Name")
        password = st.text_input("Password")

        if st.button("Create Employee"):

            if emp_code and emp_name and password:

                new_row = pd.DataFrame([{
                    "EmployeeCode":emp_code,
                    "EmployeeName":emp_name,
                    "Password":password
                }])

                employee_df = pd.concat([employee_df,new_row],ignore_index=True)
                employee_df.to_excel(EMPLOYEE_FILE,index=False)

                st.success("Employee Created")

    elif menu=="All Employees":
        st.title("All Employees")
        st.dataframe(employee_df,use_container_width=True)

    elif menu=="All Stores":
        st.title("All Stores")
        st.dataframe(gst_df,use_container_width=True)

    elif menu=="All Visit Plans":

        st.title("All Employee Visit Plans")

        if not planned_df.empty:

            employee_list = ["All"] + sorted(
                planned_df["EmployeeName"].dropna().astype(str).unique().tolist()
            )

            selected_employee = st.selectbox("Employee Filter",employee_list)

            display_df = planned_df.copy()

            if selected_employee != "All":
                display_df = display_df[display_df["EmployeeName"] == selected_employee]

            st.dataframe(display_df,use_container_width=True)

            with open(PLANNED_FILE,"rb") as f:
                st.download_button(
                    "Download All Visit Plans",
                    f,
                    file_name="All_Employee_Visit_Plans.xlsx"
                )

else:

    employee_code = st.session_state.emp_code
    employee_name = st.session_state.emp_name

    st.sidebar.title(employee_name)

    menu = st.sidebar.radio("Menu",["Beat Plan","Add New Store"])

    if menu=="Add New Store":

        st.title("Add New Store")

        gst_no = st.text_input("GST Number")
        city = st.text_input("City")
        store_name = st.text_input("Store Name")

        if st.button("Save Store"):

            gst_no = gst_no.upper().strip()

            if not validate_gst(gst_no):
                st.error("Invalid GST Number")

            elif gst_df["GSTNumber"].astype(str).str.upper().eq(gst_no).any():
                st.error("GST Already Exists")

            else:

                next_id = f"S{len(gst_df)+1:05}"

                new_store = pd.DataFrame([{
                    "StoreID":next_id,
                    "StoreName":store_name.upper(),
                    "GSTNumber":gst_no,
                    "City":city.upper(),
                    "EmployeeCode":employee_code
                }])

                gst_df = pd.concat([gst_df,new_store],ignore_index=True)
                gst_df.to_excel(GST_FILE,index=False)

                st.success("Store Added Successfully")

    else:

        st.title("Beat Plan")

        employee_stores = gst_df[
            gst_df["EmployeeCode"].astype(str)==str(employee_code)
        ]

        if employee_stores.empty:
            st.warning("No Stores Available")
            st.stop()

        city = st.selectbox(
            "City",
            sorted(employee_stores["City"].dropna().astype(str).unique())
        )

        visit_date = st.date_input("Visit Date", value=date.today())

        stores_df = employee_stores[
            employee_stores["City"].astype(str)==city
        ].copy()

        stores_df["Display"] = (
            stores_df["StoreName"].astype(str)
            + " (" +
            stores_df["StoreID"].astype(str)
            + ")"
        )

        planned_store_ids = planned_df[
            (planned_df["EmployeeCode"].astype(str)==str(employee_code))
            &
            (planned_df["VisitDate"].dt.date==visit_date)
        ]["StoreID"].astype(str).tolist()

        available_stores = stores_df[
            ~stores_df["StoreID"].astype(str).isin(planned_store_ids)
        ]

        st.subheader("Pending Stores")

        pending_stores = available_stores[
            ["StoreID","StoreName","City","GSTNumber"]
        ]

        st.dataframe(pending_stores,use_container_width=True)

        if available_stores.empty:
            st.success("All stores already planned for selected date.")
        else:

            selected_store = st.selectbox(
                "Store",
                available_stores["Display"]
            )

            if st.button("Save Visit"):

                row = available_stores[
                    available_stores["Display"]==selected_store
                ].iloc[0]

                store_id = str(row["StoreID"])

                duplicate = planned_df[
                    (planned_df["EmployeeCode"].astype(str)==str(employee_code))
                    &
                    (planned_df["StoreID"].astype(str)==store_id)
                    &
                    (planned_df["VisitDate"].dt.date==visit_date)
                ]

                if duplicate.empty:

                    new_visit = pd.DataFrame([{
                        "EmployeeCode":employee_code,
                        "EmployeeName":employee_name,
                        "City":city,
                        "Store":row["StoreName"],
                        "StoreID":store_id,
                        "VisitDate":pd.to_datetime(visit_date),
                        "Planned":True
                    }])

                    planned_df = pd.concat(
                        [planned_df,new_visit],
                        ignore_index=True
                    )

                    planned_df.to_excel(PLANNED_FILE,index=False)

                    st.success("Visit Saved")
                    st.rerun()

                else:
                    st.warning("Visit Already Planned")

        st.subheader("My Visits")

        my_visits = planned_df[
            planned_df["EmployeeCode"].astype(str)==str(employee_code)
        ]

        st.dataframe(my_visits,use_container_width=True)
