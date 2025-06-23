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

# State lists (now used for filtering only)
KARNATAKA_STATES = ['karnataka']
MP_MAHA_STATES = [
    'madhya pradesh', 'maharashtra', 'andhra pradesh',
    'telangana', 'rajasthan', 'uttar pradesh',
    'odisha', 'haryana'
]

def clean_columns(df):
    """Standardize column names: strip, lowercase, replace special chars"""
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r'[/\s]', '_', regex=True)
    )
    return df

def get_sheet_data_as_df(sheet_url, worksheet_index=0):
    """Returns DataFrame from Google Sheet"""
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_url(sheet_url)
    worksheet = spreadsheet.get_worksheet(worksheet_index)
    df = get_as_dataframe(worksheet)
    return clean_columns(df)

@app.get("/read-sheet/")
def read_sheet(sheet_url: str):
    try:
        # Get and process data
        df = get_sheet_data_as_df(sheet_url)
        
        # Clean state column
        df['state'] = df['state'].astype(str).str.strip().str.lower()
        
        # Filter data
        df_karnataka = df[df['state'].isin(KARNATAKA_STATES)]
        df_mp_maha = df[df['state'].isin(MP_MAHA_STATES)]
        
        # Return JSON data without reindexing
        return {
            "entire_data": df.fillna("").to_dict(orient="records"),
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
        df = clean_columns(df)
        
        # Clean state column
        df['state'] = df['state'].astype(str).str.strip().str.lower()
        
        # Filter data
        df_karnataka = df[df['state'] == 'karnataka']
        df_mp_maha = df[df['state'].isin(MP_MAHA_STATES)]
        
        # Return JSON data without reindexing
        return {
            "entire_data": df.fillna("").to_dict(orient="records"),
            "karnataka": df_karnataka.fillna("").to_dict(orient="records"),
            "mp_maha": df_mp_maha.fillna("").to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
