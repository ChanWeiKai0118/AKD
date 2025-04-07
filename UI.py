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
    
    if sheet_name == "chemo_data":
        sheet = client.open("web data").worksheet("chemo_data")
        row = ["" for _ in range(57)]  
        row[1], row[3], row[2], row[4], row[5] = data[0], data[1], data[2], data[3], data[4]
    
        if data[6] != 0:
            row[6], row[7] = data[5], 0
        else:
            row[6], row[7] = 0, data[5]
    
        row[9], row[12], row[54] = data[6], data[7], data[8]
        
        # 抓之前的資料
        all_rows = sheet.get_all_values() 
        last_row = len(all_rows) + 1
    
        row[0] = f'=IF(ROW()=2, 1, IF(COUNTIF(B$2:B{last_row-1}, B{last_row}) = 0, MAX(A$2:A{last_row-1}) + 1, IF(OR(H{last_row}<INDEX(H$2:H{last_row-1}, MAX(IF($B$2:B{last_row-1}=B{last_row}, ROW($B$2:B{last_row-1})-1, 0))),G{last_row}<INDEX(G$2:G{last_row-1}, MAX(IF($B$2:B{last_row-1}=B{last_row}, ROW($B$2:B{last_row-1})-1, 0))),F{last_row} - INDEX(F$2:F{last_row-1}, MAX(IF($B$2:B{last_row-1} = B{last_row}, ROW($B$2:B{last_row-1}) - 1, 0))) > 42), MAX(A$2:A{last_row-1}) + 1, INDEX(A$2:A{last_row-1}, MAX(IF(B$2:B{last_row-1}=B{last_row}, ROW($B$2:B{last_row-1})-1, 0))))))'
    
        row[8] = f'=IF(COUNTIF(A$2:A{last_row}, A{last_row}) = 1, 0, (F{last_row} - INDEX(F$2:F{last_row}, MATCH(A{last_row}, A$2:A{last_row}, 0)))/7)'
    
        row[10] = f'=SUMIF(A$2:A{last_row}, A{last_row}, J$2:J{last_row})'
        row[11] = f'=IF(OR(G{last_row}=0, K{last_row}=0), 0, K{last_row} / G{last_row})'
        row[13] = f'=SUMIF(A$2:A{last_row}, A{last_row}, M$2:M{last_row})'
        row[14] = f'=IF(OR(H{last_row}=0, N{last_row}=0), 0, N{last_row} / H{last_row})'
        row[15] = f'=IF(MATCH(B{last_row}, B$2:B{last_row}, 0) = ROW()-1, Q{last_row}, INDEX(P$2:P{last_row-1}, MATCH(B{last_row}, B$2:B{last_row-1}, 0)))'
        row[16] = f'=IFNA(INDEX(lab_data!H:H, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!H:H <> "")))) * (lab_data!H:H <> ""), 0)), "")'
        row[17] = f'=IFNA(IF(Q{last_row}="", "", INDEX(lab_data!H:H, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!H:H <> "")))) * (lab_data!H:H <> ""), 0)))-INDEX(lab_data!H:H, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = LARGE(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!H:H <> "")),2)) * (lab_data!H:H <> ""), 0)))'
        row[18] = f'=IF(Q{last_row}="", "", Q{last_row} - P{last_row})'
        row[19] = f'=IF(MATCH(B{last_row}, B$2:B{last_row}, 0) = ROW()-1, U{last_row}, INDEX(T$2:T{last_row-1}, MATCH(B{last_row}, B$2:B{last_row-1}, 0)))'
        row[20] = f'=IFNA(INDEX(lab_data!J:J, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!J:J <> "")))) * (lab_data!J:J <> ""), 0)), "")'
        row[21] = f'=IFNA(IF(U{last_row}="", "", INDEX(lab_data!J:J, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!J:J <> "")))) * (lab_data!J:J <> ""), 0)))-INDEX(lab_data!J:J, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = LARGE(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!J:J <> "")),2)) * (lab_data!J:J <> ""), 0)))'
        row[22] = f'=IF(U{last_row}="", "", U{last_row} - T{last_row})'
        row[23] = f'=IF(MATCH(B{last_row}, B$2:B{last_row}, 0) = ROW()-1, Y{last_row}, INDEX(X$2:X{last_row-1}, MATCH(B{last_row}, B$2:B{last_row-1}, 0)))'
        row[24] = f'=IFNA(INDEX(lab_data!K:K, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!K:K <> "")))) * (lab_data!K:K <> ""), 0)), "")'
        row[25] = f'=IFNA(IF(Y{last_row}="", "", INDEX(lab_data!K:K, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!K:K <> "")))) * (lab_data!K:K <> ""), 0)))-INDEX(lab_data!K:K, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = LARGE(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!K:K <> "")),2)) * (lab_data!K:K <> ""), 0)))'
        row[26] = f'=IF(Y{last_row}="", "", Y{last_row} - X{last_row})'
        row[27] = f'=IF(MATCH(B{last_row}, B$2:B{last_row}, 0) = ROW()-1, AC{last_row}, INDEX(AB$2:AB{last_row-1}, MATCH(B{last_row}, B$2:B{last_row-1}, 0)))'
        row[28] = f'=IFNA(INDEX(lab_data!G:G, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!G:G <> "")))) * (lab_data!G:G <> ""), 0)), "")'
        row[29] = f'=IFNA(IF(AC{last_row}="", "", INDEX(lab_data!G:G, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!G:G <> "")))) * (lab_data!G:G <> ""), 0)))-INDEX(lab_data!G:G, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = LARGE(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!G:G <> "")),2)) * (lab_data!G:G <> ""), 0)))'
        row[30] = f'=IF(AC{last_row}="", "", AC{last_row} - AB{last_row})'
        row[31] = f'=IF(MATCH(B{last_row}, B$2:B{last_row}, 0) = ROW()-1, AG{last_row}, INDEX(AF$2:AF{last_row-1}, MATCH(B{last_row}, B$2:B{last_row-1}, 0)))'
        row[32] = f'=IFNA(INDEX(lab_data!I:I, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!I:I <> "")))) * (lab_data!I:I <> ""), 0)), "")'
        row[33] = f'=IFNA(IF(AG{last_row}="", "", INDEX(lab_data!I:I, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!I:I <> "")))) * (lab_data!I:I <> ""), 0)))-INDEX(lab_data!I:I, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = LARGE(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!I:I <> "")),2)) * (lab_data!I:I <> ""), 0)))'
        row[34] = f'=IF(AG{last_row}="", "", AG{last_row} - AF{last_row})'
        row[35] = f'=IF(MATCH(B{last_row}, B$2:B{last_row}, 0) = ROW()-1, AK{last_row}, INDEX(AJ$2:AJ{last_row-1}, MATCH(B{last_row}, B$2:B{last_row-1}, 0)))'
        row[36] = f'=IFNA(INDEX(lab_data!L:L, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!L:L <> "")))) * (lab_data!L:L <> ""), 0)), "")'
        row[37] = f'=IFNA(IF(AK{last_row}="", "", INDEX(lab_data!L:L, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!L:L <> "")))) * (lab_data!L:L <> ""), 0)))-INDEX(lab_data!L:L, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = LARGE(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!L:L <> "")),2)) * (lab_data!L:L <> ""), 0)))'
        row[38] = f'=IF(AK{last_row}="", "", AK{last_row} - AJ{last_row})'
        row[39] = f'=IF(MATCH(B{last_row}, B$2:B{last_row}, 0) = ROW()-1, AO{last_row}, INDEX(AN$2:AN{last_row-1}, MATCH(B{last_row}, B$2:B{last_row-1}, 0)))'
        row[40] = f'=IFNA(INDEX(lab_data!M:M, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!M:M <> "")))) * (lab_data!M:M <> ""), 0)), "")'
        row[41] = f'=IFNA(IF(AO{last_row}="", "", INDEX(lab_data!M:M, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!M:M <> "")))) * (lab_data!M:M <> ""), 0)))-INDEX(lab_data!M:M, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = LARGE(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!M:M <> "")),2)) * (lab_data!M:M <> ""), 0)))'
        row[42] = f'=IF(AO{last_row}="", "", AO{last_row} - AN{last_row})'
        row[43] = f'=IF(MATCH(B{last_row}, B$2:B{last_row}, 0) = ROW()-1, AS{last_row}, INDEX(AR$2:AR{last_row-1}, MATCH(B{last_row}, B$2:B{last_row-1}, 0)))'
        row[44] = f'=IFNA(INDEX(lab_data!N:N, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!N:N <> "")))) * (lab_data!N:N <> ""), 0)), "")'
        row[45] = f'=IFNA(IF(AS{last_row}="", "", INDEX(lab_data!N:N, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = MAX(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!N:N <> "")))) * (lab_data!N:N <> ""), 0)))-INDEX(lab_data!N:N, MATCH(1, (lab_data!A:A = B{last_row}) * (lab_data!E:E = LARGE(FILTER(lab_data!E:E, (lab_data!A:A = B{last_row}) * (lab_data!E:E <= F{last_row}) * (lab_data!E:E >= F{last_row} - 30) * (lab_data!N:N <> "")),2)) * (lab_data!N:N <> ""), 0)))'
        row[46] = f'=IF(AS{last_row}="", "", AS{last_row} - AR{last_row})'
        row[52] = f'=IFNA(IF(MAX(FILTER(lab_data!H:H, (lab_data!A:A = B{last_row}) * (lab_data!E:E > F{last_row}) * (lab_data!E:E <= F{last_row} + 14)))=0, "", MAX(FILTER(lab_data!H:H, (lab_data!A:A = B{last_row}) * (lab_data!E:E > F{last_row}) * (lab_data!E:E <= F{last_row} + 14)))), "")'
        row[53] = f'=IF(BA{last_row}="", "", IF(D{last_row}=0, IF(BA{last_row}<=0.7, 141*((BA{last_row}/0.7)^-0.329)*0.993^E{last_row}*1.018, 141*((BA{last_row}/0.7)^-1.209)*0.993^E{last_row}*1.018), IF(BA{last_row}<=0.9, 141*((BA{last_row}/0.9)^-0.411)*0.993^E{last_row}, 141*((BA{last_row}/0.9)^-1.209)*0.993^E{last_row})))'
        row[55] = f'=IF(BA{last_row}="", "", IF(D{last_row}=1,IF(Q{last_row}>=1.3,IF(OR(BA{last_row}/P{last_row}>=1.5, BA{last_row}/Q{last_row}>=1.5), 1, 0),IF(OR(BA{last_row}/P{last_row}>=1.5, BA{last_row}/Q{last_row}>=1.5, BA{last_row}/1.3>=1.5), 1, 0)),IF(Q{last_row}>=1.1,IF(OR(BA{last_row}/P{last_row}>=1.5, BA{last_row}/Q{last_row}>=1.5), 1, 0),IF(OR(BA{last_row}/P{last_row}>=1.5, BA{last_row}/Q{last_row}>=1.5, BA{last_row}/1.1>=1.5), 1, 0))))'

        # AKI_history判定
        # 取得目前病人 ID 和給藥日期
        current_id = data[0]
        current_date = data[4]
        has_aki_history = False
        try:
            current_date_obj = datetime.strptime(current_date, "%Y/%m/%d")
            for r in reversed(all_rows[1:]):  # 排除標題列
                id_match = r[1] == current_id
                try:
                    prev_date_obj = datetime.strptime(r[5], "%Y/%m/%d")  # F 欄是第 6 欄 (index=5)
                except:
                    continue
        
                if id_match and prev_date_obj < current_date_obj:
                    if r[56] == "1":  # BD 是 index 56（即第 57 欄）
                        has_aki_history = True
                        break
        except Exception as e:
            print("Date parsing error:", e)
        
        # 設定 AKI history 欄位（row[54]）
        row[54] = 1 if data[8] or has_aki_history else 0
        print(f"has_aki_history for ID {current_id} on {current_date}: {has_aki_history}")
    
        sheet.append_row(row, value_input_option="USER_ENTERED")

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

col1, col2 = st.columns(2)

with col1:
    number = st.text_input("Patient ID (chemotherapy data)")
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

    chemo_data_list = [number, gender_value, weight, age, treatment_date_str, cycle_no, cis_dose, carb_dose, int(aki_history)]
    save_to_gsheet(chemo_data_list, "chemo_data")

    st.success("✅ Data submitted successfully!")

st.subheader("Predicted Risk:")
st.write("📊 (模型預測結果顯示區域，未來可填入模型輸出)")

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
