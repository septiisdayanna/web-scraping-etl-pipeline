from utils.extract import scrape_product
from utils.transform import clean_and_transform, extract_product_data
from utils.load import save_to_csv, save_to_gsheet, store_to_postgre

def main():
    BASE_URL = [
        'https://fashion-studio.dicoding.dev/',
        'https://fashion-studio.dicoding.dev/page{}'
    ]

    products_data = scrape_product(BASE_URL, extract_product_data)
    cleaned_df = clean_and_transform(products_data)

    # Simpan ke CSV
    save_to_csv(cleaned_df)

    # Simpan ke Google Sheets
    save_to_gsheet(cleaned_df, spreadsheet_id='', range_name='Sheet1!A1')

    # Simpan data ke PostgreSQL
    store_to_postgre(cleaned_df, db_url= '')  # Memanggil fungsi untuk menyimpan ke database

if __name__ == "__main__":
    main()
