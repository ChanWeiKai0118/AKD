import json
import streamlit as st
from google.oauth2.service_account import Credentials
import gspread
import datetime
import os

# 測試 API 連接
def test_google_sheets():
    try:
        creds_dict = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
        creds = Credentials.from_service_account_info(creds_dict)
        client = gspread.authorize(creds)

        # 取得 Google Sheets
        sheet = client.open("web data").worksheet("chemo data")
        print("✅ 成功連接 Google Sheets！")
    except Exception as e:
        print("❌ 連接失敗，錯誤訊息：", e)



def get_gsheet_client():
    creds = Credentials.from_service_account_info(st.secrets["google_service_account"])
    client = gspread.authorize(creds)
    return client

def save_to_gsheet(data):
    client = get_gsheet_client()
    sheet = client.open("web data").worksheet("chemo data")  # 选择 chemo data 这个 Sheet
    sheet.append_row(data)  # 追加数据到最后一行

# Streamlit UI
st.title("Chemotherapy Data Entry")

# 输入栏位
id_no = st.text_input("Patient ID")  
gender = st.selectbox("Gender", ["Male", "Female"])  
weight = st.number_input("Weight (kg)", min_value=0.0, format="%.1f")  
age = st.number_input("Age", min_value=0)  
treatment_date = st.date_input("Treatment Date", datetime.date.today())  # 直接输入日期
cycle_no = st.number_input("Cycle Number", min_value=1)  
cis_dose = st.number_input("Cisplatin Dose (mg)", min_value=0.0, format="%.1f")  
carb_dose = st.number_input("Carboplatin Dose (mg)", min_value=0.0, format="%.1f")  
aki_history = st.checkbox("AKI History (Check if Yes)")  

if st.button("Submit"):
    test_google_sheets()
    data = [id_no, gender, weight, age, str(treatment_date), cycle_no, cis_dose, carb_dose, int(aki_history)]
    save_to_gsheet(data)
    st.success("✅ Data submitted successfully!")
