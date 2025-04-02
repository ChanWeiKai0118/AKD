import json
import streamlit as st
from google.oauth2.service_account import Credentials
import gspread
import datetime

# 設定 Google Sheets API 權限範圍
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

def get_gsheet_client():
    try:
        creds_dict = json.loads(st.secrets["google_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"❌ Google Sheets 連接失敗: {e}")
        return None

def save_to_gsheet(data):
    client = get_gsheet_client()
    if client:
        try:
            sheet = client.open("web data").worksheet("chemo data")
            sheet.append_row(data)
            st.success("✅ Data submitted successfully!")
        except Exception as e:
            st.error(f"❌ 無法寫入 Google Sheets: {e}")

# Streamlit UI
st.title("Chemotherapy Data Entry")

# 使用者輸入欄位
id_no = st.text_input("Patient ID")  
gender = st.selectbox("Gender", ["Male", "Female"])  
weight = st.number_input("Weight (kg)", min_value=0.0, format="%.1f")  
age = st.number_input("Age", min_value=0)  
treatment_date = st.date_input("Treatment Date", datetime.date.today())
cycle_no = st.number_input("Cycle Number", min_value=1)  
cis_dose = st.number_input("Cisplatin Dose (mg)", min_value=0.0, format="%.1f")  
carb_dose = st.number_input("Carboplatin Dose (mg)", min_value=0.0, format="%.1f")  
aki_history = st.checkbox("AKI History (Check if Yes)")  

if st.button("Submit"):
    save_to_gsheet([id_no, gender, weight, age, str(treatment_date), cycle_no, cis_dose, carb_dose, int(aki_history)])
