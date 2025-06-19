from fastapi import FastAPI, UploadFile, File, HTTPException
from io import BytesIO
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe
import os

app = FastAPI()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SERVICE_ACCOUNT_FILE = os.environ.get("SERVICE_ACCOUNT_FILE")

# Standardized template columns (lowercase, no special characters)
template_columns_mp_mh = [
    'state', 'district', 'tehsil', 'mandal', 'village', 'village_lgd_code',
    'id', 'village_match_status', 'survey_match_status',
    'state_ss_initial', 'district_ss_initial', 'tehsil_ss_initial', 'tehsil_id',
    'village_ss_initial', 'lgd_code_ss', 'confidence_score',
    'soundex_check', 'survey_number', 'survey_id', 'geometry_id'
]

template_columns_ktk = [
    'state', 'district', 'taluk', 'hobli', 'village', 'village_lgd_code',
    'id', 'village_match_status', 'survey_match_status',
    'state_ss_initial', 'district_ss_initial', 'taluk_ss_initial', 'taluk_id',
    'village_ss_initial', 'lgd_code_ss', 'confidence_score',
    'soundex_check', 'survey_number', 'survey_id', 'geometry_id'
]

def clean_columns(df):
    """Standardize column names: strip, lowercase, replace special chars"""
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r'[/\s]', '_', regex=True)  # Replace spaces/special chars
    )
    return df

def get_sheet_data_as_df(sheet_url, worksheet_index=0):
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_url(sheet_url)
    worksheet = spreadsheet.get_worksheet(worksheet_index)
    df = get_as_dataframe(worksheet)
    df = clean_columns(df)  # Clean columns immediately
    df['state'] = df['state'].astype(str).str.strip().str.lower()
    return df

@app.get("/read-sheet/")
def read_sheet(sheet_url: str):
    karnataka_states = ['karnataka']
    mp_maha_states = ['madhya pradesh', 'maharashtra']
    try:
        df = get_sheet_data_as_df(sheet_url)
        df_karnataka = df[df['state'].isin(karnataka_states)].reindex(columns=template_columns_ktk)
        df_mp_maha = df[df['state'].isin(mp_maha_states)].reindex(columns=template_columns_mp_mh)
        return {
            "karnataka": df_karnataka.fillna("").to_dict(orient="records"),
            "mp_maha": df_mp_maha.fillna("").to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/upload_excel/")
async def upload_excel(file: UploadFile = File(...)):
    try:
        content = await file.read()
        df = pd.read_excel(BytesIO(content))
        df = clean_columns(df)  # Apply same cleaning
        df['state'] = df['state'].astype(str).str.strip().str.lower()
        df_karnataka = df[df['state'] == 'karnataka'].reindex(columns=template_columns_ktk)
        df_mp_maha = df[df['state'].isin(['madhya pradesh', 'maharashtra'])].reindex(columns=template_columns_mp_mh)
        return {
            "karnataka": df_karnataka.fillna("").to_dict(orient="records"),
            "mp_maha": df_mp_maha.fillna("").to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
