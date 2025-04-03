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

def save_to_gsheet(data, sheet_name):
    client = get_gsheet_client()
    sheet = client.open("web data").worksheet(sheet_name)
    sheet.append_row(data, value_input_option="USER_ENTERED")

# --- 第一個 UI (化療數據) ---
st.title("Chemotherapy Data Entry")

col1, col2 = st.columns(2)

with col1:
    number = st.text_input("Patient ID")
    weight = st.number_input("Weight (kg)", min_value=0.0, format="%.1f")
    gender = st.selectbox("Gender", ["Male", "Female"])
    gender_value = 1 if gender == "Male" else 0
    age = st.number_input("Age", min_value=0)

with col2:
    treatment_date = st.date_input("Treatment Date", datetime.date.today())
    cycle_no = st.number_input("Cycle Number", min_value=1)
    cis_dose = st.number_input("Cisplatin Dose (mg)", min_value=0.0, format="%.1f")
    carb_dose = st.number_input("Carboplatin Dose (mg)", min_value=0.0, format="%.1f")
    aki_history = st.checkbox("AKI History (Check if Yes)")

if st.button("Predict"):
    treatment_date_str = treatment_date.strftime("%Y/%m/%d")
    chemo_data = [number, gender_value, weight, age, treatment_date_str, cycle_no, cis_dose, carb_dose, int(aki_history)]
    save_to_gsheet(chemo_data, "chemo data")
    st.success("✅ Chemotherapy data submitted successfully!")

st.subheader("Predicted Risk:")
st.write("📊 (模型預測結果顯示區域，未來可填入模型輸出)")

# --- 第二個 UI (檢驗數據) ---
st.title("Laboratory Data Entry")

col3, col4 = st.columns(2)

with col3:
    lab_number = st.text_input("Patient ID (Lab Data)")
    weight_lab = st.number_input("Weight (kg) - Lab", min_value=0.0, format="%.1f")
    lab_date = st.date_input("Date", datetime.date.today())

with col4:
    bun = st.number_input("BUN", min_value=0.0, format="%.1f", value=None)
    scr = st.number_input("Scr", min_value=0.0, format="%.2f", value=None)
    hgb = st.number_input("Hgb", min_value=0.0, format="%.1f", value=None)
    sodium = st.number_input("Sodium (N)", min_value=0.0, format="%.1f", value=None)
    potassium = st.number_input("Potassium (K)", min_value=0.0, format="%.1f", value=None)

if st.button("Submit Lab Data"):
    lab_date_str = lab_date.strftime("%Y/%m/%d")

    lab_data = [
        lab_number, "", "", weight_lab, lab_date_str, "", "", bun or "", scr or "", "", "", hgb or "", sodium or "", potassium or ""
    ]
    
    save_to_gsheet(lab_data, "lab data")
    st.success("✅ Laboratory data submitted successfully!")
