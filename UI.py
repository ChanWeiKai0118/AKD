import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

def get_gsheet_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file("your-service-account.json", scopes=scope)
    client = gspread.authorize(creds)
    return client

def save_to_gsheet(data):
    client = get_gsheet_client()
    sheet = client.open("web data").worksheet("chemo data")
    sheet.append_row(data)

# Streamlit UI
st.markdown("### Enter patient details below to predict AKD probability:")
# Input form
with st.form("AKD_form"):
    col1, col2 = st.columns(2)

    with col1:
        number = st.text_input("Patient ID")
        gender = st.selectbox("Gender", ["Male", "Female"])
        weight = st.number_input("Weight (kg)", min_value=0.0,step=0.1, format="%.2f")
        age = st.number_input("Age", min_value=0,step=1, format="%d")
    
    with col2:
        treatment_date = st.date_input("Treatment Date")
        cycle_no = st.number_input("Cycle Number", min_value=1, format="%d")
        cis_dose = st.number_input("Cisplatin Dose (mg)", min_value=0.0, format="%.2f")
        carb_dose = st.number_input("Carboplatin Dose (mg)", min_value=0.0, format="%.2f")
        aki_history = st.checkbox("AKI History (Check if Yes)")

    submitted = st.form_submit_button("Predict")

if st.button("Submit"):
    data = [id_no, gender, weight, age, str(treatment_date), cycle_no, cis_dose, carb_dose, int(aki_history)]
    save_to_gsheet(data)
    st.success("Data submitted successfully!")
