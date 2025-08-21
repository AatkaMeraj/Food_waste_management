# Food Waste Manager App 

# Pages:
#   1) Filter & Explore
#   2) Contact (Providers / Receivers)
#   3) CRUD (Add / Update / Delete)
#   4) SQL Query (type queries and get answers)

# DB:
#  MySQL database: food_mng_db
#  Primary table: merged_data

# --------------------------------------------------------------

# IMPORT LIBRARIES
import os
from datetime import date, datetime, timedelta
import re
from typing import Dict, List

import pandas as pd
import streamlit as st
import plotly.express as px
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

# CONFIGURATION

st.set_page_config(
    page_title="Food Waste Manager",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# GLOBAL STYLE
CUSTOM_CSS = """
<style>
:root {
  --bg: #0b1020; --card:#121833; --muted:#8aa0ff; --accent:#6cf0c2; --accent2:#ffd166;
}
/* dark gradient backdrop */
body {background: radial-gradient(80% 120% at 20% 0%, #111936 0%, #0b1020 40%, #0b1020 100%) no-repeat fixed;}
.block-container {padding-top: 1.2rem;}
h1,h2,h3,h4 { color: #e6e9ff; }

/***** Cards *****/
section[data-testid="stSidebar"] {background: linear-gradient(180deg,#10152b,#0c1227);}
.stMetric {background: rgba(255,255,255,.06); border-radius: 14px; padding: 10px;}

/***** Buttons *****/
.stButton>button, .stDownloadButton>button {border-radius: 12px; font-weight: 700; border: 1px solid rgba(255,255,255,.15); box-shadow: 0 10px 24px rgba(0,0,0,.25);}

/***** Inputs *****/
.stSelectbox, .stTextInput, .stTextArea, .stNumberInput, .stDateInput {color: #e6e9ff;}

/***** Tables *****/
.dataframe {border-radius: 12px; overflow: hidden;}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# TITLE
CENTER_TITLE = """
<style>
.centered-title {
    text-align: center;
    color: #003366; /* Dark Blue */
    font-size: 2.5rem;
    font-weight: 800;
}
</style>
"""
st.markdown(CENTER_TITLE, unsafe_allow_html=True)
st.markdown('<h1 class="centered-title">Food Waste Manager</h1>', unsafe_allow_html=True)



# DATABASE CONNECTION

# Default DB values from env vars
DEFAULT_DB = os.getenv("FD_DB_NAME", "")
DEFAULT_HOST = os.getenv("FD_DB_HOST", "localhost")
DEFAULT_USER = os.getenv("FD_DB_USER", "root")
DEFAULT_PORT = int(os.getenv("FD_DB_PORT", "3306"))
TABLE_NAME = os.getenv("FD_TABLE", "")

# --- LOGIN CHECK ---
if "engine" not in st.session_state:
    
    # Show login page
    st.markdown(
    "<h3 style='color:black; text-align:center;font-size:22px;'>Connect to MySQL Database</h3>",
    unsafe_allow_html=True
    )

    # adjust the form in the centre
    col1, col2, col3 = st.columns([1, 2, 1])  

    with col2:  # Center column
        with st.form("db_connect_form"):
            host = st.text_input("Host", value=DEFAULT_HOST)
            port = st.number_input("Port", 1, 65535, value=DEFAULT_PORT)
            user = st.text_input("User", value=DEFAULT_USER)
            password = st.text_input("Password", type="password")
            database = st.text_input("Database", value=DEFAULT_DB)
            table = st.text_input("Table", value=TABLE_NAME)

            connect_btn = st.form_submit_button("Connect")

            if connect_btn:
                try:
                    st.session_state["engine"] = create_engine(
                        f"mysql+pymysql://{user}:{password}@{host}:{int(port)}/{database}?charset=utf8mb4",
                        pool_pre_ping=True,
                    )
                    st.session_state["db_info"] = {"database": database, "table": table}
                    st.success("Connected successfully! Reloading...")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Connection failed: {e}")

    st.stop()

# Check if engine is created
engine: Engine | None = st.session_state.get("engine")
if engine is None:
    st.info("Enter your MySQL credentials above and click **Connect**.")
    st.stop()

# HELPERS

def q(sql: str, params: Dict | None = None):
    with engine.begin() as con:
        return con.execute(text(sql), params or {})

def df(sql: str, params: Dict | None = None) -> pd.DataFrame:
    with engine.begin() as con:
        return pd.read_sql(text(sql), con=con, params=params or {})

# Detect available columns and provide aliases
db_info = st.session_state.get("db_info", {})
table = db_info.get("table", "")

if table:
    query = f"SELECT * FROM {table} LIMIT 1"
    df_preview = df(query)
    cols = df_preview.columns.tolist() if not df_preview.empty else []
else:
    cols = []

    
def pick(*candidates: str, default: str | None = None):
    for cand in candidates:
        for c in cols:
            if c.lower() == cand.lower():
                return c
    return default

COL = {
    "id": pick("Claim_ID", "Food_ID"),
    "location": pick("Location", "City", "City_receiver"),
    "provider_name": pick("Name_Provider", "Provider_ID"),
    "provider_type": pick("Provider_Type", "Type"),
    "provider_phone": pick("Contact"),
    "receiver_name": pick("Name_receiver", "Receiver_ID"),
    "receiver_type": pick("Type_receiver"),
    "receiver_phone": pick("Contact_receiver"),
    "food_name": pick("Food_Name"),
    "food_type": pick("Food_Type", "Meal_Type"),
    "quantity": pick("Quantity"),
    "expiry_date": pick("Expiry_Date"),
    "status": pick("Status"),
    "created_at": pick("Timestamp"),
    "address": pick("Address"),
}


# SIDEBAR NAVIGATION

with st.sidebar:
    
    page = st.radio(
        "Select an Option",
        ["Filter & Explore", "Contact", "CRUD", "SQL Query Studio"],
        label_visibility="visible",
    )
    st.markdown("---")
    st.caption(f"DB: **{st.session_state['db_info']['database']}** · Table: **{table}**")

# FILTER & EXPLORE PAGE

if page == "Filter & Explore":
    st.markdown(
    "<h3 style='color:black; text-align:center;font-size:22px;'>Filter & Explore</h3>",
    unsafe_allow_html=True
    )

    # Build dynamic filters
    def distinct(col):
        if col:
            return df(f"SELECT DISTINCT {col} AS v FROM {table} WHERE {col} IS NOT NULL ORDER BY 1")
        return pd.DataFrame({"v": []})

    c1, c2, c3, c4 = st.columns(4)
    loc_sel = c1.multiselect("Location", distinct(COL["location"])['v'].tolist() if COL['location'] else [])
    prov_sel = c2.multiselect("Provider", distinct(COL["provider_name"])['v'].tolist() if COL['provider_name'] else [])
    food_sel = c3.multiselect("Food Type", distinct(COL["food_type"])['v'].tolist() if COL['food_type'] else [])
    status_sel = c4.multiselect("Status", ["available","assigned","picked","expired"]) if COL['status'] else []

    where = ["1=1"]; params={}
    if loc_sel and COL['location']: where.append(f"{COL['location']} IN :loc"), params.update({"loc": tuple(loc_sel)})
    if prov_sel and COL['provider_name']: where.append(f"{COL['provider_name']} IN :prov"), params.update({"prov": tuple(prov_sel)})
    if food_sel and COL['food_type']: where.append(f"{COL['food_type']} IN :food"), params.update({"food": tuple(food_sel)})
    if status_sel and COL['status']: where.append(f"{COL['status']} IN :sts"), params.update({"sts": tuple(status_sel)})

    sel_cols = [c for c in [COL['id'], COL['provider_name'], COL['receiver_name'], COL['food_type'],
                            COL['quantity'], COL['expiry_date'], COL['location'], COL['status']] if c]

    sql = f"SELECT {', '.join(sel_cols)} FROM {table} WHERE {' AND '.join(where)} ORDER BY {sel_cols[-1]} DESC"
    data = df(sql, params)

    # Display filters
    if COL['expiry_date'] and not data.empty:
        data['days_to_expiry'] = (pd.to_datetime(data[COL['expiry_date']]) - pd.Timestamp.today().normalize()).dt.days

    st.dataframe(data, use_container_width=True, hide_index=True)

    st.download_button("⬇️ Download CSV", data=data.to_csv(index=False).encode("utf-8"), file_name=f"filtered_{date.today()}.csv")

# CONTACT PAGE

elif page == "Contact":
    st.markdown(
    "<h3 style='color:black; text-align:center;font-size:22px;'>Contact Providers/ Receivers</h3>",
    unsafe_allow_html=True
    )
    
    which = st.radio("Whom to contact?", ["Provider", "Receiver"], horizontal=True)

    if which == "Provider":
        name_col, address_col, phone_col = COL['provider_name'], COL['address'], COL['provider_phone']
    else:
        name_col, phone_col = COL['receiver_name'], COL['receiver_phone']
        address_col = None

    if not name_col:
        st.error("Required columns not found in table.")
    else:
        # Fetch contacts from DB
        query = f"SELECT DISTINCT {name_col} AS name"
        if address_col:
            query += f", {address_col} AS address"
        query += f", {phone_col or 'NULL'} AS phone FROM {table} WHERE {name_col} IS NOT NULL ORDER BY 1"
        
        contacts = df(query)

        person = st.selectbox("Select contact", ["-- Not in list, enter manually --"] + contacts['name'].tolist())

        if person == "-- Not in list, enter manually --":
            person = st.text_input("Enter Name")
            if which == "Provider":
                address = st.text_input("Enter Address (optional)")
            else:
                address = None
            phone = st.text_input("Enter Phone")
        else:
            info = contacts[contacts['name'] == person].iloc[0]
            phone = info['phone'] if pd.notna(info['phone']) else None
            address = info['address'] if address_col and pd.notna(info['address']) else None

        # Show contact info if available
        if person:
            st.markdown(f"**Name:** {person}")
            if address:
                st.markdown(f"**Address:** {address}")
            st.markdown(f"**Phone:** [{phone}](tel:{phone})" if phone else "**Phone:** —")
            
    st.caption("Click phone links to contact them directly.")

# CRUD PAGE

elif page == "CRUD":
    st.markdown(
    "<h3 style='color:black; text-align:center;font-size:22px;'>CRUD (Create, Remove, Update & Delete)</h3>",
    unsafe_allow_html=True
    )

    # Initialize data 
    if "merged_data" not in st.session_state:
        try:
            st.session_state.merged_data = df(f"SELECT * FROM {table}")
        except Exception:
            st.session_state.merged_data = pd.DataFrame(columns=[
                'Claim_ID', 'Food_ID', 'Receiver_ID', 'Status', 'Timestamp',
       'Food_Name', 'Quantity', 'Expiry_Date', 'Provider_ID', 'Provider_Type',
       'Location', 'Food_Type', 'Meal_Type', 'Name', 'Type', 'Address', 'City',
       'Contact', 'Name_receiver', 'Type_receiver', 'City_receiver',
       'Contact_receiver'
            ])

    merged_df = st.session_state.merged_data.copy()

    crud_choice = st.radio("Choose operation:", ["Insert", "Update", "Delete"])

    # Insert
    if crud_choice == "Insert":
        with st.form("insert_form"):
            new_row = {}
            for col in merged_df.columns:
                new_row[col] = st.text_input(f"Enter {col}")
            submitted = st.form_submit_button("Insert Row")
            if submitted:
                merged_df = merged_df.append(new_row, ignore_index=True)
                st.session_state.merged_data = merged_df
                st.success("Row inserted successfully!")

    # Update
    elif crud_choice == "Update":
        if not merged_df.empty:
            row_index = st.number_input("Enter row index to update:", min_value=0, max_value=len(merged_df)-1, step=1)
            with st.form("update_form"):
                updated_row = {}
                for col in merged_df.columns:
                    updated_row[col] = st.text_input(f"Update {col}", value=str(merged_df.at[row_index, col]))
                submitted = st.form_submit_button("Update Row")
                if submitted:
                    for col in merged_df.columns:
                        merged_df.at[row_index, col] = updated_row[col]
                    st.session_state.merged_data = merged_df
                    st.success("Row updated successfully!")
        else:
            st.warning("No data available to update.")

    # Delete
    elif crud_choice == "Delete":
        if not merged_df.empty:
            row_index = st.number_input(
                "Enter row index to delete:", 
                min_value=0, 
                max_value=len(merged_df)-1, 
                step=1
            )

            # Display the row before deleting
        
            st.dataframe(merged_df.iloc[[row_index]])

            # Confirmation step
            confirm_delete = st.radio(
                "Are you sure you want to delete this row?", 
                ("Yes", "No"), 
                horizontal=True
            )

            if st.button("Delete Row"):
                if confirm_delete == "Yes":
                    merged_df = merged_df.drop(row_index).reset_index(drop=True)
                    st.session_state.merged_data = merged_df
                    st.success("Row deleted successfully!")
                else:
                    st.info("Deletion cancelled.")
        else:
            st.warning("No data available to delete.")


 
# SQL QUERY STUDIO PAGE

elif page == "SQL Query Studio":
    st.markdown(
    "<h3 style='color:black; text-align:center;font-size:22px;'>SQL Query Studio</h3>",
    unsafe_allow_html=True
    )
   

    query = st.text_area("Write your SQL Query here", value=f"SELECT * FROM {table} LIMIT 10", height=160)
    allow_write = st.checkbox("Allow INSERT/UPDATE/DELETE", value=False)

    if st.button("Run", use_container_width=True):
        try:
            if not allow_write and not re.match(r"^\s*select", query, re.I):
                st.warning("Only SELECT queries are allowed unless you enable write mode.")
            else:
                if re.match(r"^\s*select", query, re.I):
                    out = df(query)
                    st.success(f"Returned {len(out)} rows.")
                    st.dataframe(out, use_container_width=True)
                    # Quick chart if two cols
                    if len(out.columns) >= 2 and out.dtypes[1] in ["int64","float64"]:
                        fig = px.bar(out.iloc[:50], x=out.columns[0], y=out.columns[1], title="Preview Chart")
                        st.plotly_chart(fig, use_container_width=True)
                    st.download_button("⬇Download results", out.to_csv(index=False).encode("utf-8"), file_name="query_results.csv")
                else:
                    q(query)
                    st.success("Query executed.")
        except Exception as e:
            st.error(f"Query error: {e}")


