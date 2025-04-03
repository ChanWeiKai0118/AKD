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
    row = ["" for _ in range(57)]  
    row[1], row[3], row[2], row[4], row[5] = data[0], data[1], data[2], data[3], data[4]

    if data[6] != 0:
        row[6], row[7] = data[5], 0
    else:
        row[6], row[7] = 0, data[5]

    row[9], row[12], row[54] = data[6], data[7], data[8]

    last_row = len(sheet.get_all_values()) + 1

    row[0] = f'=IF(ROW()=2, 1, IF(COUNTIF(B$2:B{last_row-1}, B{last_row}) = 0, MAX(A$2:A{last_row-1}) + 1, IF(OR(H{last_row}<INDEX(H$2:H{last_row-1}, MAX(IF($B$2:B{last_row-1}=B{last_row}, ROW($B$2:B{last_row-1})-1, 0))),G{last_row}<INDEX(G$2:G{last_row-1}, MAX(IF($B$2:B{last_row-1}=B{last_row}, ROW($B$2:B{last_row-1})-1, 0))),F{last_row} - INDEX(F$2:F{last_row-1}, MAX(IF($B$2:B{last_row-1} = B{last_row}, ROW($B$2:B{last_row-1}) - 1, 0))) > 42), MAX(A$2:A{last_row-1}) + 1, INDEX(A$2:A{last_row-1}, MAX(IF(B$2:B{last_row-1}=B{last_row}, ROW($B$2:B{last_row-1})-1, 0))))))'

    row[8] = f'=IF(COUNTIF(A$2:A{last_row}, A{last_row}) = 1, 0, (F{last_row} - INDEX(F$2:F{last_row}, MATCH(A{last_row}, A$2:A{last_row}, 0)))/7)'

    row[10] = f'=SUMIF(A$2:A{last_row}, A{last_row}, J$2:J{last_row})'
    row[11] = f'=IF(OR(G{last_row}=0, K{last_row}=0), 0, K{last_row} / G{last_row})'
    row[13] = f'=SUMIF(A$2:A{last_row}, A{last_row}, M$2:M{last_row})'
    row[14] = f'=IF(OR(H{last_row}=0, N{last_row}=0), 0, N{last_row} / H{last_row})'
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

def save_to_gsheet2(data, sheet_name):
    client = get_gsheet_client()
    sheet = client.open("web data").worksheet(sheet_name)
    row = ["" for _ in range(14)]  
    row[0], row[3], row[4] = data[0], data[1], data[2]

    row[6], row[7], row[11], row[12], row[13] = data[3], data[4], data[5], data[6], data[7]

  
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
    lab_data = [lab_number, weight_lab, lab_date_str, bun or "", scr or "", hgb or "", sodium or "", potassium or ""]
    save_to_gsheet2(lab_data, "lab data")
    st.success("✅ Laboratory data submitted successfully!")
