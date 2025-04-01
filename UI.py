# streamlit_app.py

import streamlit as st
from streamlit_gsheets import GSheetsConnection
url = "https://docs.google.com/spreadsheets/d/1G-o0659UDZQp2_CFEzty8mI0VXXYWzA0rc7v-Uz1ccc/edit?gid=0#gid=0"
# Create a connection object.
conn = st.experimental_connection("gsheets", type=GSheetsConnection)

data = conn.read(spreadsheet=url, usecols[0,1])
st.dataframe(data)
