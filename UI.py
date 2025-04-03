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

    # 讀取整張試算表的內容
    values = sheet.get_all_values()

    # 找到第一個可以填入的 row
    empty_row_index = None
    for i, row in enumerate(values, start=1):  # start=1 讓索引與試算表行數對齊
        if all(row[x] == "" for x in [1, 2, 3, 4, 5, 6, 7, 9, 12, 54]):  # 檢查要填的欄位是否為空
            empty_row_index = i
            break

    # 如果找不到空白行，就加到最後一行
    if empty_row_index is None:
        empty_row_index = len(values) + 1

    # 設定要填入的資料
    row_data = ["" for _ in range(57)]  # 預留 57 個欄位
    row_data[1] = data[0]   # B: number
    row_data[3] = data[1]   # D: gender
    row_data[2] = data[2]   # C: weight
    row_data[4] = data[3]   # E: age
    row_data[5] = data[4]   # F: treatment_date_str

    if data[6] != 0:
        row_data[6] = data[5]  # G: cycle_no
        row_data[7] = 0        # H: 空值
    else:
        row_data[6] = 0        # G: 空值
        row_data[7] = data[5]  # H: cycle_no

    row_data[9] = data[6]   # J: cis_dose
    row_data[12] = data[7]  # M: carb_dose
    row_data[54] = data[8]  # BC: aki_history

    # 更新 Google 試算表的特定行
    sheet.update(f"A{empty_row_index}:BE{empty_row_index}", [row_data], value_input_option="USER_ENTERED")


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
    
    data = [number, gender_value, weight, age, treatment_date_str, cycle_no, cis_dose, carb_dose, int(aki_history)] 
    save_to_gsheet(data)
    
    st.success(f"✅ Data submitted successfully!")
