import json
import streamlit as st
from google.oauth2.service_account import Credentials
import gspread
import datetime

def get_gsheet_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["google_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    return client

def save_to_gsheet(data):
    client = get_gsheet_client()
    sheet = client.open("web data").worksheet("chemo data")
    
    row = ["" for _ in range(56)]  # BD欄是第56欄
    row[1] = data[0]   # B: id_no
    row[3] = data[1]   # E: gender
    row[2] = data[2]   # D: weight
    row[4] = data[3]   # F: age
    row[6] = data[4]   # G: treatment_date_str
    row[5] = data[5]   # H: treatment_date_value
    
    if data[7] != 0:
        row[7] = data[6]  # I: cycle_no
        row[8] = 0
    else:
        row[7] = 0
        row[8] = data[6]  # I: cycle_no

    row[10] = data[7]  # K: cis_dose
    row[13] = data[8]  # N: carb_dose
    row[55] = data[9]  # BD: aki_history
    
    sheet.append_row(row)

# Streamlit UI
st.title("Chemotherapy Data Entry")

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
    treatment_date_str = treatment_date.strftime("%Y/%m/%d")  # 轉換為 YYYY/MM/DD 格式
    excel_date = (treatment_date - datetime.date(1899, 12, 30)).days  # 計算 Excel 日期值
    
    data = [id_no, gender, weight, age, treatment_date_str, excel_date, cycle_no, cis_dose, carb_dose, int(aki_history)]
    save_to_gsheet(data)
    
    st.success(f"✅ Data submitted successfully!")
