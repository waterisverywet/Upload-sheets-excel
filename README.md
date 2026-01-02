# Google Sheets & Excel Data Processing API

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0-green)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

> A powerful REST API for processing and filtering Google Sheets and Excel files with regional data organization

## 📋 Overview

Google Sheets & Excel Data Processing API is a FastAPI-based application designed to handle spreadsheet data imports from Google Sheets and Excel files. It provides intelligent data filtering and organization by geographic regions, specifically optimized for Indian state-level data processing.

### Key Features

- **Google Sheets Integration**: Direct access to Google Sheets via service account authentication
- **Excel Upload Support**: Upload and process Excel files (.xlsx, .xls)
- **Intelligent Data Filtering**: Organize data by geographic regions (Karnataka, MP-Maharashtra cluster)
- **JSON Output**: Convert spreadsheet data to structured JSON format
- **Data Standardization**: Automatic column name cleaning and normalization
- **RESTful API**: Simple HTTP endpoints for data processing
- **Error Handling**: Comprehensive error responses with detailed messages

## 🛠️ Tech Stack

- **Framework**: FastAPI (modern async Python web framework)
- **Data Processing**: Pandas (data manipulation)
- **Google Integration**: Google OAuth2 & gspread (Sheets access)
- **Excel Processing**: openpyxl (Excel file handling)
- **Server**: Uvicorn (ASGI server)
- **Utilities**: python-multipart (file upload handling)

## 📋 Prerequisites

- Python 3.8 or higher
- Google Cloud Project with Sheets API enabled
- Service account JSON file from Google Cloud
- Internet connection for Google Sheets access

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/waterisverywet/Upload-sheets-excel.git
cd Upload-sheets-excel
```

### 2. Create Virtual Environment

```bash
# Using venv
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\\Scripts\\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Credentials

Create a `.env` file in the project root:

```env
SERVICE_ACCOUNT_FILE=path/to/service-account-key.json
```

Alternatively, set the environment variable:

```bash
export SERVICE_ACCOUNT_FILE=/path/to/service-account-key.json
```

**Obtaining Service Account Key**:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable Google Sheets API
4. Create a Service Account
5. Generate and download a JSON key file
6. Share the Google Sheet with the service account email

## 📖 Usage

### Running the Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation

Interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔌 API Endpoints

### 1. Read Google Sheet

**Endpoint**: `GET /read-sheet/`

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sheet_url` | string | Yes | URL of the Google Sheet |

**Example Request**:

```bash
curl -X GET "http://localhost:8000/read-sheet/?sheet_url=https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"
```

**Response** (HTTP 200):

```json
{
  "entire_data": [
    {
      "id": 1,
      "name": "John Doe",
      "state": "karnataka"
    }
  ],
  "karnataka": [
    {
      "id": 1,
      "name": "John Doe",
      "state": "karnataka"
    }
  ],
  "mp_maha": []
}
```

### 2. Upload Excel File

**Endpoint**: `POST /upload_excel/`

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | file | Yes | Excel file (.xlsx or .xls) |

**Example Request**:

```bash
curl -X POST "http://localhost:8000/upload_excel/" \
  -F "file=@path/to/your/file.xlsx"
```

**Response** (HTTP 200):

```json
{
  "entire_data": [...],
  "karnataka": [...],
  "mp_maha": [...]
}
```

**Error Responses**:

- **400 Bad Request**: Invalid file format or missing required columns
- **500 Internal Server Error**: Server-side processing error

## 📊 Data Filtering Logic

The API automatically filters data into three categories:

1. **Karnataka**: Records where state column equals 'karnataka'
2. **MP-Maharashtra Cluster**: Records matching states:
   - Madhya Pradesh
   - Maharashtra
   - Andhra Pradesh
   - Telangana
   - Rajasthan
   - Uttar Pradesh
   - Odisha
   - Haryana
3. **Entire Data**: All records from the source

## 🏗️ Project Structure

```
Upload-sheets-excel/
├── main.py                    # Main FastAPI application
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── Dockerfile                # Docker container configuration
├── docker-compose.yml        # Docker Compose setup
└── README.md                 # This file
```

## 🔄 Data Processing Pipeline

1. **Column Standardization**
   - Strip whitespace from column names
   - Convert to lowercase
   - Replace spaces and special characters with underscores

2. **State Normalization**
   - Convert state values to lowercase
   - Strip whitespace

3. **Data Filtering**
   - Filter by Karnataka
   - Filter by MP-Maharashtra cluster
   - Keep entire dataset

4. **JSON Conversion**
   - Convert to record-oriented JSON
   - Replace NaN values with empty strings

## 🐳 Docker Deployment

### Build Docker Image

```bash
docker build -t sheets-excel-api .
```

### Run Container

```bash
docker run -p 8000:8000 \
  -e SERVICE_ACCOUNT_FILE=/app/service-account-key.json \
  -v /path/to/service-account-key.json:/app/service-account-key.json \
  sheets-excel-api
```

### Using Docker Compose

```bash
docker-compose up
```

Make sure to update `.env` with your credentials before running.

## 🔐 Security Considerations

- **Service Account Key**: Never commit service account keys to version control
- **API Keys**: Use environment variables for sensitive data
- **File Uploads**: Validate file types and sizes
- **Access Control**: Implement authentication for production use
- **CORS**: Configure CORS properly for production

## 📝 Example Workflow

```python
# Reading from Google Sheet
import requests

sheet_url = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"
response = requests.get(
    "http://localhost:8000/read-sheet/",
    params={"sheet_url": sheet_url}
)

data = response.json()
karnataka_records = data["karnataka"]
maha_mp_records = data["mp_maha"]
```

## 🛠️ Troubleshooting

### Service Account Authentication Error

**Problem**: "Unable to open spreadsheet"

**Solution**:
- Verify service account email has access to the sheet
- Check SERVICE_ACCOUNT_FILE path is correct
- Ensure Google Sheets API is enabled

### Column Not Found Error

**Problem**: "KeyError: 'state'"

**Solution**:
- Ensure your Excel/Sheet has a 'state' column
- Check column names are properly formatted
- Use the data cleaning functions

### File Upload Fails

**Problem**: "File format not supported"

**Solution**:
- Use .xlsx or .xls file formats
- Ensure file is not corrupted
- Check file size is reasonable

## 📧 Dependencies

- **fastapi** (0.104.1): Web framework
- **uvicorn** (0.24.0): ASGI server
- **pandas** (0.24.0): Data manipulation
- **gspread** (3.0.0): Google Sheets API client
- **gspread-dataframe**: DataFrame integration with gspread
- **google-auth** (2.0.0+): Google authentication
- **openpyxl**: Excel file handling
- **python-multipart**: File upload support

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

[@waterisverywet](https://github.com/waterisverywet)

## 📞 Support

For issues, questions, or suggestions, please open an issue on the [GitHub repository](https://github.com/waterisverywet/Upload-sheets-excel/issues).

---

**Last Updated**: January 2026
