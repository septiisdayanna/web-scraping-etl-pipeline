import pandas as pd # untuk manipulasi data
from google.oauth2.service_account import Credentials # untuk autentikasi Google Sheets
from googleapiclient.discovery import build # untuk mengakses Google Sheets API
from sqlalchemy import create_engine # untuk membuat koneksi dengan database PostgreSQL

def save_to_csv(df, filepath="products.csv"):
    """Fungsi untuk menyimpan data ke dalam CSV."""
    try:
        df.to_csv(filepath, index=False)
        print(f"Data berhasil disimpan ke {filepath}")
    except Exception as e:
        print(f"Gagal menyimpan data: {e}")



def save_to_gsheet(df, spreadsheet_id, range_name='Sheet1!A1', credentials_file='google-sheets-api.json'):
    """Fungsi untuk menyimpan data ke dalam Google Sheets."""
    try:
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        credential = Credentials.from_service_account_file(credentials_file, scopes=scopes)
        service = build('sheets', 'v4', credentials=credential)

        # Ubah DataFrame ke list of lists
        values = [df.columns.tolist()] + df.astype(str).values.tolist()
        body = {'values': values}

        # Kirim ke Google Sheets
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()

        print("Data berhasil ditambahkan ke Google Sheets!")
    except Exception as e:
        print(f"Gagal menyimpan data ke Google Sheets: {e}")
 


def store_to_postgre(df, db_url):
    """Fungsi untuk menyimpan data ke dalam PostgreSQL."""
    try:
        # Membuat engine database
        engine = create_engine(db_url)
        
        # Menyimpan data ke tabel 'productstoscrape' jika tabel sudah ada, data akan ditambahkan (append)
        with engine.connect() as con:
            df.to_sql('productstoscrape', con=con, if_exists='append', index=False)
            print("Data berhasil ditambahkan ke PostgreSQL!")
    
    except Exception as e:
        print(f"Terjadi kesalahan saat menyimpan data ke PostgreSQL: {e}")