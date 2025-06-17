from fastapi import FastAPI, UploadFile, File, HTTPException
from io import BytesIO
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe
import os  # <-- Add this import

app = FastAPI()

# Google Sheets API settings
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SERVICE_ACCOUNT_FILE = os.environ.get("/etc/secrets/SERVICE_ACCOUNT_FILE")  # <-- Use env variable

# Column templates
template_columns_mp_mh = ['State', 'District', 'Tehsil', 'Mandal', 'Village', 'Village LGD Code']
template_columns_ktk = ['State', 'District', 'Tehsil', 'Hobli', 'Village', 'Village LGD Code']

def get_sheet_data_as_df(sheet_url, worksheet_index=0):
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_url(sheet_url)
    worksheet = spreadsheet.get_worksheet(worksheet_index)
    df = get_as_dataframe(worksheet)
    df.columns = df.columns.str.strip()
    df['State'] = df['State'].astype(str).str.strip().str.lower()
    return df

@app.get("/read-sheet/")
def read_sheet(sheet_url: str):
    karnataka_states = ['karnataka']
    mp_maha_states = ['madhya pradesh', 'maharashtra']
    try:
        df = get_sheet_data_as_df(sheet_url)
        df.columns = df.columns.str.strip()
        df['State'] = df['State'].astype(str).str.strip().str.lower()
        df_karnataka = df[df['State'].isin(karnataka_states)].reindex(columns=template_columns_ktk)
        df_mp_maha = df[df['State'].isin(mp_maha_states)].reindex(columns=template_columns_mp_mh)
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
        df.columns = df.columns.str.strip()
        df['State'] = df['State'].astype(str).str.strip().str.lower()
        df_karnataka = df[df['State'] == 'karnataka'].reindex(columns=template_columns_ktk)
        df_mp_maha = df[df['State'].isin(['madhya pradesh', 'maharashtra'])].reindex(columns=template_columns_mp_mh)
        return {
            "karnataka": df_karnataka.fillna("").to_dict(orient="records"),
            "mp_maha": df_mp_maha.fillna("").to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
