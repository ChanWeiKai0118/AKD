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

    row = ["" for _ in range(56)]  # BD欄是第55欄 

    # A欄 (id_no)：使用 Excel 公式
    last_row = len(sheet.get_all_values()) + 1  # 獲取當前行數
    if last_row == 2:  # 第一筆資料 (Excel 第一行是標題，第二行開始為資料)
        row[0] = 1  # 第一筆 id_no 設為 1
    else:
        row[0] = f'=IF(OR(B{last_row}<>B{last_row-1},H{last_row-1}<H{last_row-2}, I{last_row-1}<I{last_row-2}, AND(H{last_row-1}>0, I{last_row-1}>0)), A{last_row-1}+1, A{last_row-1})'

    # 其他欄位
    row[1] = data[0]  # B: number
    row[3] = data[1]  # D: gender (已轉換為 1/0)
    row[2] = data[2]  # C: weight
    row[4] = data[3]  # E: age
    row[6] = data[4]  # G: treatment_date_str
    row[5] = data[5]  # F: treatment_date_value
    
    if data[7] != 0:
        row[7] = data[6]  # H: cycle_no
        row[8] = 0
    else:
        row[7] = 0
        row[8] = data[6]  # I: cycle_no 

    row[10] = data[7]  # K: cis_dose
    row[13] = data[8]  # N: carb_dose
    row[55] = data[9]  # BD: aki_history
    
    sheet.append_row(row, value_input_option="USER_ENTERED")  # 允許輸入 Excel 公式

# Streamlit UI
st.title("Chemotherapy Data Entry")

number = st.text_input("Patient ID")   
gender = st.selectbox("Gender", ["Male", "Female"])  
gender_value = 1 if gender == "Male" else 0  # 轉換性別數值
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
    
    data = [number, gender_value, weight, age, treatment_date_str, excel_date, cycle_no, cis_dose, carb_dose, int(aki_history)] 
    save_to_gsheet(data)
    
    st.success(f"✅ Data submitted successfully!")
