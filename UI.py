import json
import streamlit as st
from google.oauth2.service_account import Credentials
import gspread
import datetime
import pandas as pd
import numpy as np
from tensorflow import keras
from sklearn.preprocessing import MinMaxScaler
import joblib
import requests, zipfile, io
from tensorflow.keras.saving import load_model
import sklearn
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.metrics import AUC
from keras.models import load_model

#超重要，model的threshold
optimal_threshold = 0.29


# Load the model
def get_model():
    url = "https://raw.githubusercontent.com/ChanWeiKai0118/AKD/main/AKD-LSTM.zip"
    response = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(response.content))
    z.extractall(".")
    model = load_model("AKD-LSTM.keras", compile=False)
    return model

model = get_model()

# Load the scaler
scaler_url = "https://raw.githubusercontent.com/ChanWeiKai0118/AKD/main/akd_scaler.pkl"
scaler_response = requests.get(scaler_url)
with open("akd_scaler.pkl", "wb") as scaler_file:
    scaler_file.write(scaler_response.content)
normalizer = joblib.load("akd_scaler.pkl")

# Load the imputation
url = "https://raw.githubusercontent.com/ChanWeiKai0118/AKD/main/akd_miceforest.zip"
r = requests.get(url)
z = zipfile.ZipFile(io.BytesIO(r.content))
z.extractall(".")
miceforest = joblib.load("akd_miceforest.pkl")

target_columns = [
    'id_no', 'age', 'treatment_duration', 'cis_dose', 'cis_cum_dose',
    'average_cis_cum_dose', 'carb_cum_dose', 'baseline_hemoglobin',
    'baseline_bun', 'baseline_bun/scr', 'baseline_egfr', 'baseline_sodium',
    'baseline_potassium', 'latest_hemoglobin', 'latest_scr', 'latest_crcl',
    'bun_change', 'crcl_change', 'bun/scr_slope', 'crcl_slope', 'aki_history']
cols_for_preprocessing = [
    'id_no', 'age', 'treatment_duration', 'cis_dose', 'cis_cum_dose',
    'average_cis_cum_dose', 'carb_cum_dose', 'baseline_hemoglobin',
    'baseline_bun', 'baseline_bun/scr', 'baseline_egfr', 'baseline_sodium',
    'baseline_potassium', 'latest_hemoglobin', 'latest_scr', 'latest_crcl',
    'bun_change', 'crcl_change', 'bun/scr_slope', 'crcl_slope', 'aki_history',
    'akd']
selected_features = [
    'age', 'treatment_duration', 'cis_dose', 'cis_cum_dose',
    'average_cis_cum_dose', 'carb_cum_dose', 'baseline_hemoglobin',
    'baseline_bun', 'baseline_bun/scr', 'baseline_egfr', 'baseline_sodium',
    'baseline_potassium', 'latest_hemoglobin', 'latest_scr', 'latest_crcl',
    'bun_change', 'crcl_change', 'bun/scr_slope', 'crcl_slope', 'aki_history']

def post_sequential_padding( # (for return_sequences True)
        data, groupby_col, selected_features, outcome, maxlen
    ):
    grouped = data.groupby(groupby_col)
    sequences = []
    labels = []
    for name, group in grouped:
        sequences.append(group[selected_features].values)
        labels.append(group[[outcome]].values)

    X = pad_sequences(
        sequences,
        maxlen=maxlen,
        dtype='float32',
        padding='post',
        truncating='post',
        value=-1
    )

    y = pad_sequences(
        labels,
        maxlen=maxlen,
        padding='post',
        truncating='post',
        value=-1
    )

    return X, y
        
def preprocessing(
        data, scaler, imputer, cols_for_preprocessing,
        selected_features, groupby_col, outcome, maxlen
    ):
    # passing arguments
    test = data
    scaler_ = scaler
    imputer_ = imputer

    # feature selection
    test_selected = test[cols_for_preprocessing]

    # imputation
    test_imputed = test_selected.copy()
    test_imputed[selected_features] = imputer_.transform(test_selected[selected_features])

    # scaling
    test_scaled = test_imputed.copy()
    test_scaled[selected_features] = scaler_.transform(test_imputed[selected_features])

    # sequential padding
    X_test, y_test = post_sequential_padding(
        data=test_scaled,
        groupby_col=groupby_col,
        selected_features=selected_features,
        outcome=outcome,
        maxlen=maxlen
    )

    return X_test, y_test

def get_gsheet_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["google_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    return client

def save_to_gsheet(data, sheet_name):
    client = get_gsheet_client()
    
    if sheet_name == "chemo_data":
        sheet = client.open("web data").worksheet("chemo_data")
        row = ["" for _ in range(57)]  
        row[1], row[3], row[2], row[4], row[5] = data[0], data[1], data[2], data[3], data[4]
    
        if data[6] != 0:
            row[6], row[7] = data[5], 0
        else:
            row[6], row[7] = 0, data[5]
    
        row[9], row[12] = data[6], data[7]
        
        # 抓之前的資料
        all_rows = sheet.get_all_values() 
        last_row = len(all_rows) + 1
    
        row[0] = f'=IF(ROW()=2, 1, IF(COUNTIF(B$2:B{last_row-1}, B{last_row}) = 0, MAX(A$2:A{last_row-1}) + 1, IF(OR(H{last_row}<INDEX(H$2:H{last_row-1}, MAX(IF($B$2:B{last_row-1}=B{last_row}, ROW($B$2:B{last_row-1})-1, 0))),G{last_row}<INDEX(G$2:G{last_row-1}, MAX(IF($B$2:B{last_row-1}=B{last_row}, ROW($B$2:B{last_row-1})-1, 0))),F{last_row} - INDEX(F$2:F{last_row-1}, MAX(IF($B$2:B{last_row-1} = B{last_row}, ROW($B$2:B{last_row-1}) - 1, 0))) > 42), MAX(A$2:A{last_row-1}) + 1, INDEX(A$2:A{last_row-1}, MAX(IF(B$2:B{last_row-1}=B{last_row}, ROW($B$2:B{last_row-1})-1, 0))))))'
    
        row[8] = f'=IF(COUNTIF(A$2:A{last_row}, A{last_row}) = 1, 0, (F{last_row} - INDEX(F$2:F{last_row}, MATCH(A{last_row}, A$2:A{last_row}, 0)))/7)'
    
        row[10] = f'=SUMIF(A$2:A{last_row}, A{last_row}, J$2:J{last_row})'
        row[11] = f'=IF(OR(G{last_row}=0, K{last_row}=0), 0, K{last_row} / G{last_row})'
        row[13] = f'=SUMIF(A$2:A{last_row}, A{last_row}, M$2:M{last_row})'
        row[14] = f'=IF(OR(H{last_row}=0, N{last_row}=0), 0, N{last_row} / H{last_row})'
        row[15] = f'=IF(MATCH(B{last_row}, B$2:B{last_row}, 0) = ROW()-1,IF(Q{last_row} <> "", Q{last_row},IFNA(INDEX(lab_data!H:H,MATCH(1,(lab_data!A:A = B{last_row}) *(lab_data!E:E = MAX(FILTER(lab_data!E:E,(lab_data!A:A = B{last_row}) *(lab_data!E:E <= F{last_row}) *(lab_data!E:E >= F{last_row} - 90) *(lab_data!H:H <> "")))),0)), "")),INDEX(P$2:P{last_row-1}, MATCH(B{last_row}, B$2:B{last_row-1}, 0)))'
        row[16] = f'=IFNA(INDEX(lab_data!H:H, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!H:H <> "")))) * (lab_data!H:H <> ""), 0)), "")'
        row[17] = f'=IFNA(IF(Q{last_row}="", "", INDEX(lab_data!H:H, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!H:H <> "")))) * (lab_data!H:H <> ""), 0))-INDEX(lab_data!H:H, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = LARGE(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 90) * (lab_data!H:H <> "")),2)) * (lab_data!H:H <> ""), 0))))'
        row[18] = f'=IF(Q{last_row}="", "", Q{last_row} - P{last_row})'
        row[19] = f'=IF(MATCH(B{last_row}, B$2:B{last_row}, 0) = ROW()-1,IF(U{last_row} <> "", U{last_row},IFNA(INDEX(lab_data!J:J,MATCH(1,(lab_data!A:A = B{last_row}) *(lab_data!E:E = MAX(FILTER(lab_data!E:E,(lab_data!A:A = B{last_row}) *(lab_data!E:E <= F{last_row}) *(lab_data!E:E >= F{last_row} - 90) *(lab_data!J:J <> "")))),0)), "")),INDEX(T$2:T{last_row-1}, MATCH(B{last_row}, B$2:B{last_row-1}, 0)))'
        row[20] = f'=IFNA(INDEX(lab_data!J:J, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!J:J <> "")))) * (lab_data!J:J <> ""), 0)), "")'
        row[21] = f'=IFNA(IF(U{last_row}="", "", INDEX(lab_data!J:J, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!J:J <> "")))) * (lab_data!J:J <> ""), 0))-INDEX(lab_data!J:J, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = LARGE(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 90) * (lab_data!J:J <> "")),2)) * (lab_data!J:J <> ""), 0))))'
        row[22] = f'=IF(U{last_row}="", "", U{last_row} - T{last_row})'
        row[23] = f'=IF(MATCH(B{last_row}, B$2:B{last_row}, 0) = ROW()-1,IF(Y{last_row} <> "", Y{last_row},IFNA(INDEX(lab_data!K:K,MATCH(1,(lab_data!A:A = B{last_row}) *(lab_data!E:E = MAX(FILTER(lab_data!E:E,(lab_data!A:A = B{last_row}) *(lab_data!E:E <= F{last_row}) *(lab_data!E:E >= F{last_row} - 90) *(lab_data!K:K <> "")))),0)), "")),INDEX(X$2:X{last_row-1}, MATCH(B{last_row}, B$2:B{last_row-1}, 0)))'
        row[24] = f'=IFNA(INDEX(lab_data!K:K, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!K:K <> "")))) * (lab_data!K:K <> ""), 0)), "")'
        row[25] = f'=IFNA(IF(Y{last_row}="", "", INDEX(lab_data!K:K, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!K:K <> "")))) * (lab_data!K:K <> ""), 0))-INDEX(lab_data!K:K, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = LARGE(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 90) * (lab_data!K:K <> "")),2)) * (lab_data!K:K <> ""), 0))))'
        row[26] = f'=IF(Y{last_row}="", "", Y{last_row} - X{last_row})'
        row[27] = f'=IF(MATCH(B{last_row}, B$2:B{last_row}, 0) = ROW()-1,IF(AC{last_row} <> "", AC{last_row},IFNA(INDEX(lab_data!G:G,MATCH(1,(lab_data!A:A = B{last_row}) *(lab_data!E:E = MAX(FILTER(lab_data!E:E,(lab_data!A:A = B{last_row}) *(lab_data!E:E <= F{last_row}) *(lab_data!E:E >= F{last_row} - 90) *(lab_data!G:G <> "")))),0)), "")),INDEX(AB$2:AB{last_row-1}, MATCH(B{last_row}, B$2:B{last_row-1}, 0)))'
        row[28] = f'=IFNA(INDEX(lab_data!G:G, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!G:G <> "")))) * (lab_data!G:G <> ""), 0)), "")'
        row[29] = f'=IFNA(IF(AC{last_row}="", "", INDEX(lab_data!G:G, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!G:G <> "")))) * (lab_data!G:G <> ""), 0))-INDEX(lab_data!G:G, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = LARGE(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 90) * (lab_data!G:G <> "")),2)) * (lab_data!G:G <> ""), 0))))'
        row[30] = f'=IF(AC{last_row}="", "", AC{last_row} - AB{last_row})'
        row[31] = f'=IF(MATCH(B{last_row}, B$2:B{last_row}, 0) = ROW()-1,IF(AG{last_row} <> "", AG{last_row},IFNA(INDEX(lab_data!I:I,MATCH(1,(lab_data!A:A = B{last_row}) *(lab_data!E:E = MAX(FILTER(lab_data!E:E,(lab_data!A:A = B{last_row}) *(lab_data!E:E <= F{last_row}) *(lab_data!E:E >= F{last_row} - 90) *(lab_data!I:I <> "")))),0)), "")),INDEX(AF$2:AF{last_row-1}, MATCH(B{last_row}, B$2:B{last_row-1}, 0)))'
        row[32] = f'=IFNA(INDEX(lab_data!I:I, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!I:I <> "")))) * (lab_data!I:I <> ""), 0)), "")'
        row[33] = f'=IFNA(IF(AG{last_row}="", "", INDEX(lab_data!I:I, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!I:I <> "")))) * (lab_data!I:I <> ""), 0))-INDEX(lab_data!I:I, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = LARGE(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 90) * (lab_data!I:I <> "")),2)) * (lab_data!I:I <> ""), 0))))'
        row[34] = f'=IF(AG{last_row}="", "", AG{last_row} - AF{last_row})'
        row[35] = f'=IF(MATCH(B{last_row}, B$2:B{last_row}, 0) = ROW()-1,IF(AK{last_row} <> "", AK{last_row},IFNA(INDEX(lab_data!L:L,MATCH(1,(lab_data!A:A = B{last_row}) *(lab_data!E:E = MAX(FILTER(lab_data!E:E,(lab_data!A:A = B{last_row}) *(lab_data!E:E <= F{last_row}) *(lab_data!E:E >= F{last_row} - 90) *(lab_data!L:L <> "")))),0)), "")),INDEX(AJ$2:AJ{last_row-1}, MATCH(B{last_row}, B$2:B{last_row-1}, 0)))'
        row[36] = f'=IFNA(INDEX(lab_data!L:L, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!L:L <> "")))) * (lab_data!L:L <> ""), 0)), "")'
        row[37] = f'=IFNA(IF(AK{last_row}="", "", INDEX(lab_data!L:L, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!L:L <> "")))) * (lab_data!L:L <> ""), 0))-INDEX(lab_data!L:L, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = LARGE(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 90) * (lab_data!L:L <> "")),2)) * (lab_data!L:L <> ""), 0))))'
        row[38] = f'=IF(AK{last_row}="", "", AK{last_row} - AJ{last_row})'
        row[39] = f'=IF(MATCH(B{last_row}, B$2:B{last_row}, 0) = ROW()-1,IF(AO{last_row} <> "", AO{last_row},IFNA(INDEX(lab_data!M:M,MATCH(1,(lab_data!A:A = B{last_row}) *(lab_data!E:E = MAX(FILTER(lab_data!E:E,(lab_data!A:A = B{last_row}) *(lab_data!E:E <= F{last_row}) *(lab_data!E:E >= F{last_row} - 90) *(lab_data!M:M <> "")))),0)), "")),INDEX(AN$2:AN{last_row-1}, MATCH(B{last_row}, B$2:B{last_row-1}, 0)))'
        row[40] = f'=IFNA(INDEX(lab_data!M:M, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!M:M <> "")))) * (lab_data!M:M <> ""), 0)), "")'
        row[41] = f'=IFNA(IF(AO{last_row}="", "", INDEX(lab_data!M:M, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!M:M <> "")))) * (lab_data!M:M <> ""), 0))-INDEX(lab_data!M:M, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = LARGE(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 90) * (lab_data!M:M <> "")),2)) * (lab_data!M:M <> ""), 0))))'
        row[42] = f'=IF(AO{last_row}="", "", AO{last_row} - AN{last_row})'
        row[43] = f'=IF(MATCH(B{last_row}, B$2:B{last_row}, 0) = ROW()-1,IF(AS{last_row} <> "", AS{last_row},IFNA(INDEX(lab_data!N:N,MATCH(1,(lab_data!A:A = B{last_row}) *(lab_data!E:E = MAX(FILTER(lab_data!E:E,(lab_data!A:A = B{last_row}) *(lab_data!E:E <= F{last_row}) *(lab_data!E:E >= F{last_row} - 90) *(lab_data!N:N <> "")))),0)), "")),INDEX(AR$2:AR{last_row-1}, MATCH(B{last_row}, B$2:B{last_row-1}, 0)))'
        row[44] = f'=IFNA(INDEX(lab_data!N:N, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!N:N <> "")))) * (lab_data!N:N <> ""), 0)), "")'
        row[45] = f'=IFNA(IF(AS{last_row}="", "", INDEX(lab_data!N:N, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!N:N <> "")))) * (lab_data!N:N <> ""), 0))-INDEX(lab_data!N:N, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = LARGE(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 90) * (lab_data!N:N <> "")),2)) * (lab_data!N:N <> ""), 0))))'
        row[46] = f'=IF(AS{last_row}="", "", AS{last_row} - AR{last_row})'
        row[52] = f'=IFNA(IF(MAX(FILTER(lab_data!H:H, (lab_data!A:A = B{last_row}) * (lab_data!E:E > F{last_row}) * (lab_data!E:E <= F{last_row} + 14)))=0, "", MAX(FILTER(lab_data!H:H, (lab_data!A:A = B{last_row}) * (lab_data!E:E > F{last_row}) * (lab_data!E:E <= F{last_row} + 14)))), "")'
        row[53] = f'=IF(BA{last_row}="", "", IF(D{last_row}=0, IF(BA{last_row}<=0.7, 141*((BA{last_row}/0.7)^-0.329)*0.993^E{last_row}*1.018, 141*((BA{last_row}/0.7)^-1.209)*0.993^E{last_row}*1.018), IF(BA{last_row}<=0.9, 141*((BA{last_row}/0.9)^-0.411)*0.993^E{last_row}, 141*((BA{last_row}/0.9)^-1.209)*0.993^E{last_row})))'
        row[55] = f'=IF(BA{last_row}="", "", IF(D{last_row}=1,IF(Q{last_row}>=1.3,IF(OR(BA{last_row}/P{last_row}>=1.5, BA{last_row}/Q{last_row}>=1.5), 1, 0),IF(OR(BA{last_row}/P{last_row}>=1.5, BA{last_row}/Q{last_row}>=1.5, BA{last_row}/1.3>=1.5), 1, 0)),IF(Q{last_row}>=1.1,IF(OR(BA{last_row}/P{last_row}>=1.5, BA{last_row}/Q{last_row}>=1.5), 1, 0),IF(OR(BA{last_row}/P{last_row}>=1.5, BA{last_row}/Q{last_row}>=1.5, BA{last_row}/1.1>=1.5), 1, 0))))'
        
        # AKI_history判定
        # 取得目前病人 ID 和給藥日期
        current_id = data[0]
        current_date = data[4]
        checkbox_checked = data[8]
        has_aki_history = False
        for r in reversed(all_rows[1:]):  # 從最新資料往回找
            if r[1] == current_id and r[5] < current_date and r[55] == "1":  # 注意：從 Google Sheet 抓下來是字串
                has_aki_history = True
                break
        if data[8] or has_aki_history : 
            row[54] = 1
        else :
            row[54] = 0  # UI 有勾 or 過去有 AKI 就是 1
        
        return row

    elif sheet_name == "lab_data":
        sheet = client.open("web data").worksheet("lab_data")
        last_row = len(sheet.get_all_values()) + 1
        row = ["" for _ in range(14)]  
        
        row[0], row[3], row[4] = data[0], data[1], data[2]
        row[6], row[7], row[11], row[12], row[13] = data[3], data[4], data[5], data[6], data[7]
        row[1] = f'=IFERROR(VLOOKUP(A{last_row}, INDIRECT("chemo_data!B:D"), 3, FALSE), "")'  # 查找性别
        row[2] = f'=IFERROR(VLOOKUP(A{last_row}, INDIRECT("chemo_data!B:E"), 4, FALSE), "")'  # 查找年紀
        # F 列: 如果 G (BUN) 有值，則填入 G，否則找最近的 BUN
        row[5] = f'=IF(G{last_row}<>"", G{last_row}, IF(ROW()=2, "", IFERROR(INDEX(G$2:G{last_row-1}, MAX(IF(A$2:A{last_row-1}=A{last_row}, ROW(A$2:A{last_row-1})-1, 0))), "")))'

        # I 列: 如果 H (Scr) 為空則為空，否則 F / H
        row[8] = f'=IF(OR(H{last_row}="", F{last_row}=""), "", F{last_row} / H{last_row})'
        # J 列: eGFR 计算
        row[9] = f'=IF(B{last_row}=0, IF(H{last_row}<=0.7, 141*((H{last_row}/0.7)^-0.329)*0.993^C{last_row}*1.018, 141*((H{last_row}/0.7)^-1.209)*0.993^H{last_row}*1.018), IF(H{last_row}<=0.9, 141*((H{last_row}/0.9)^-0.411)*0.993^C{last_row}, 141*((H{last_row}/0.9)^-1.209)*0.993^C{last_row}))'
        # K 列: CrCl 计算
        row[10] = f'=IF(B{last_row}=0, ((140 - C{last_row}) * D{last_row}) / (H{last_row} * 72) * 0.85, ((140 - C{last_row}) * D{last_row}) / (H{last_row} * 72))'

        sheet.append_row(row, value_input_option="USER_ENTERED")


# --- Streamlit UI ---
st.title("Chemotherapy Data Entry")

mode = st.radio("Select mode", options=["Predict mode", "Preview mode"], horizontal=True)

# 預測模式
if mode == "Predict mode":
    st.subheader("🔮 Prediction Mode")
    col1, col2 = st.columns(2)

    with col1:
        number_pred = st.text_input("Patient ID (chemotherapy data)", key="predict_id")
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
        chemo_data_list = [
            number, gender_value, weight, age, treatment_date_str,
            cycle_no, cis_dose, carb_dose, aki_history  # 注意這裡保留 bool (True/False)
        ]
    
        # 回傳資料行、AKI 判定結果、病人 ID
        row_to_write = save_to_gsheet(chemo_data_list, "chemo_data")
    
        # 這裡才送出資料
        sheet = get_gsheet_client().open("web data").worksheet("chemo_data")
        sheet.append_row(row_to_write, value_input_option="USER_ENTERED")
    
        st.success("✅ Data submitted successfully!")
    
        # 讀取整張表格（包含公式的計算結果）
        raw_values = sheet.get_all_values()
        
        # 將第0列視為欄位名稱，從第1列開始是資料
        headers = raw_values[0]
        data = raw_values[1:]
        
        # 建立 DataFrame（這樣可以確保取得的是計算後的值）
        df = pd.DataFrame(data, columns=headers)
        
        # 假設你剛剛 append 的是最後一列
        last_row_index = len(sheet.get_all_values())
        last_row_values = sheet.row_values(last_row_index)
        # 這裡你拿到的是公式運算後的值，不是 `'=A2'` 這種公式本身
        input_id = last_row_values[0]
    
        # 篩選相同 ID 的資料
        df_filtered = df[df['id_no'] == input_id]
        
        # 顯示輸入資料原始樣貌（僅保留指定欄位）
        cols_to_show = ['Number', 'weight', 'sex_male', 'age', 'Index_date 1(dose)', 'cis_cycle', 'carb_cycle', 'cis_dose','carb_dose']
        preview_data = df_filtered[cols_to_show].tail(6)  # 取最後6筆
        st.subheader("Data to feed into LSTM model")
        st.dataframe(preview_data)
        
        # 日期排序 + 擷取6筆資料
        df_filtered = df_filtered.sort_values(by='Index_date 1(dose)', ascending=True).tail(6)
        
        # 只取指定欄位
        input_data = df_filtered[target_columns]
        
        # 轉成數值型，非數字會變 NaN
        input_data = input_data.apply(pd.to_numeric, errors='coerce')
        input_data.reset_index(drop=True, inplace=True)
    
        #加上akd
        input_data.loc[input_data.index[-1], 'akd'] = 0
    
        #進行imputation和scaler
        X_test, y_test = preprocessing(
        data=input_data,
        scaler=normalizer,
        imputer=miceforest,
        cols_for_preprocessing=cols_for_preprocessing,
        groupby_col='id_no',
        selected_features=selected_features,
        outcome='akd',
        maxlen=6)
    
        X_test_2d = np.squeeze(X_test)  # shape (6, 39)
        X_test_df = pd.DataFrame(X_test_2d)
        
        # 计算权重，忽略 padding 部分
        sample_weight = (y_test != -1).astype(float).flatten()
        
        # 预测概率
        y_prob = model.predict(X_test)
        y_prob = y_prob.squeeze().flatten()
        
        # 过滤掉 padding 数据
        valid_indices = sample_weight > 0
        flat_prob = y_prob[valid_indices]
        last_prob = flat_prob[-1] * 100
        st.subheader(f"Predicted Risk: {last_prob:.2f}%")
# -----------------------------
# 預覽模式
elif mode == "Preview mode":
    st.subheader("🗂️ Preview Mode")
    number_preview = st.text_input("Input patient ID", key="preview_id")
    if st.button("Check"):
        if number_preview:
            try:
                client = get_gsheet_client()
                sheet = client.open("web data").worksheet("chemo_data")
                all_data = sheet.get_all_records()
                df = pd.DataFrame(all_data)

                filtered_df = df[df['Number'] == number_preview]
                preview_cols = ['id_no', 'name', 'gender', 'age', 'height', 'weight', 'bsa', 'chemo_type', 'chemo_start_date']
                
                if not filtered_df.empty:
                    st.subheader(f"Patient information（ID: {number_preview}）")
                    st.dataframe(filtered_df[preview_cols])
                else:
                    st.info("❗ The patient has no chemotherapy data")
            except Exception as e:
                st.error(f"Something wrong when loading Google Sheet ：{e}")
        else:
            st.warning("Please enter patient ID")

# --- 第二個 UI (檢驗數據) ---
st.title("Laboratory Data Entry")

col3, col4 = st.columns(2)

with col3:
    lab_number = st.text_input("Patient ID (lab data)")
    weight_lab = st.number_input("Weight (kg) - Lab", min_value=0.0, format="%.1f")
    lab_date = st.date_input("Date", datetime.date.today())

with col4:
    bun = st.number_input("BUN", min_value=0.0, value=None)
    scr = st.number_input("Scr", min_value=0.00, format="%.2f", value=None)
    hgb = st.number_input("Hgb", min_value=0.0, format="%.1f", value=None)
    sodium = st.number_input("Sodium (N)", min_value=0, value=None)
    potassium = st.number_input("Potassium (K)", min_value=0, value=None)

if st.button("Submit Lab Data"):
    lab_date_str = lab_date.strftime("%Y/%m/%d")
    lab_data_list = [lab_number, weight_lab, lab_date_str, bun or "", scr or "", hgb or "", sodium or "", potassium or ""]
    save_to_gsheet(lab_data_list, "lab_data")
    st.success("✅ Laboratory data submitted successfully!")
