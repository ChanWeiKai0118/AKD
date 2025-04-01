import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# 設定 Google Sheets API 權限
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("your_google_key.json", scope)
client = gspread.authorize(creds)

# 連接 Google Sheets
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1G-o0659UDZQp2_CFEzty8mI0VXXYWzA0rc7v-Uz1ccc/edit?usp=sharing"
sheet = client.open_by_url(spreadsheet_url).sheet1

# 讀取資料
data = sheet.get_all_records()
df = pd.DataFrame(data)

st.title("Google Sheets x Streamlit")

# 顯示目前資料
st.write("目前的 Google Sheets 資料：")
st.dataframe(df)

# 使用者輸入新資料
st.subheader("新增資料")
col1, col2 = st.columns(2)
with col1:
    new_col1 = st.text_input("欄位 1 (例如: Name)")
with col2:
    new_col2 = st.text_input("欄位 2 (例如: Age)")

if st.button("新增到 Google Sheets"):
    if new_col1 and new_col2:
        sheet.append_row([new_col1, new_col2])  # 追加新資料
        st.success("資料已新增！請重新整理查看更新。")
    else:
        st.warning("請輸入完整資料！")

# 刪除最後一列
if st.button("刪除最後一列"):
    sheet.delete_rows(len(df) + 1)  # gspread 的索引從 1 開始
    st.success("已刪除最後一列！請重新整理查看更新。")
