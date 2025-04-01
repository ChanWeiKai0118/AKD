import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
from streamlit_gsheets.gsheets_conncetion import GSheetsConnection
import pandas as pd

# 設定 Google Sheets API 權限
SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

# 透過 Streamlit Secrets 讀取 Google 憑證
CREDENTIALS_JSON = st.secrets["google_service_account"]

# 連線到 Google Sheets
def connect_to_gsheet(spreadsheet_name, sheet_name):
    creds = Credentials.from_service_account_info(CREDENTIALS_JSON, scopes=SCOPES)
    client = gspread.authorize(creds)
    spreadsheet = client.open(spreadsheet_name)
    return spreadsheet.worksheet(sheet_name)

# 設定 Google Sheets 參數
SPREADSHEET_NAME = "web data"  # 你的 Google Sheets 名稱
SHEET_NAME = "chemo data"      # 你的工作表名稱

# 連結 Google Sheets
sheet_by_name = connect_to_gsheet(SPREADSHEET_NAME, SHEET_NAME)

st.title("Simple Data Entry using Streamlit")

# 讀取 Google Sheets 的資料
def read_data():
    data = sheet_by_name.get_all_records()
    return pd.DataFrame(data)

# 顯示 Google Sheets 的資料
df = read_data()
st.dataframe(df)

# 新增資料到 Google Sheets
def add_data(row):
    sheet_by_name.append_row(row)

# 建立 Streamlit 輸入框
with st.form("data_entry"):
    col1, col2 = st.columns(2)
    name = col1.text_input("Enter Name")
    age = col2.number_input("Enter Age", min_value=1, max_value=120)

    submitted = st.form_submit_button("Submit")
    if submitted:
        add_data([name, age])
        st.success("Data added successfully!")
