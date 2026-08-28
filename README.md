# Fashion Product ETL Pipeline

## Overview
Project ini adalah pipeline ETL (Extract, Transform, Load) yang mengambil data produk fashion dari sebuah situs katalog, membersihkan dan mentransformasi datanya agar siap dianalisis, lalu menyimpannya ke tiga jenis data repository sekaligus: file CSV, Google Sheets, dan database PostgreSQL. Seluruh tahapan dibangun secara modular dan dilengkapi unit test.

## Background / Problem
Data produk pada website e-commerce sering tidak terstruktur dan tidak konsisten (harga dalam dolar, rating dalam format teks campur angka, kolom size/gender berisi teks tambahan, dsb). Mengumpulkan dan membersihkan data semacam ini secara manual memakan waktu dan rawan kesalahan. Project ini membangun pipeline otomatis yang dapat dijalankan berulang untuk mengekstrak, membersihkan, dan mendistribusikan data produk ke berbagai tujuan penyimpanan.

## Objectives
- Mengambil seluruh data produk dari situs sumber secara otomatis, termasuk menangani pagination.
- Membersihkan data agar bebas dari nilai duplikat, null, dan tidak valid.
- Mengonversi data ke format dan tipe yang konsisten (harga ke Rupiah, rating ke float, dll).
- Menyimpan data ke lebih dari satu jenis data repository agar mudah diakses tim lain.
- Memastikan setiap tahapan pipeline teruji melalui unit test.

## Features
- **Modular ETL** — extract, transform, dan load masing-masing berada di file terpisah (`extract.py`, `transform.py`, `load.py`), memudahkan pengujian dan pemeliharaan.
- **Scraping dengan pagination otomatis** — mengambil data dari seluruh halaman katalog hingga tidak ada tombol "Next" lagi, dengan throttling (delay 2 detik) antar halaman.
- **Data cleaning menyeluruh** — menghapus data tidak valid (misalnya "Unknown Product", "Price Unavailable"), duplikat, dan nilai null; mengonversi harga USD ke Rupiah (kurs Rp16.000), rating ke tipe float, colors ke tipe integer, serta membersihkan teks berlebih pada kolom size dan gender.
- **Timestamp otomatis** — setiap baris data dilengkapi waktu ekstraksi.
- **Error handling di setiap fungsi** — baik saat request gagal, data tidak valid, maupun proses penyimpanan gagal, pipeline tidak crash melainkan mencatat pesan error dan melanjutkan proses.
- **Penyimpanan ke tiga repository sekaligus** — CSV lokal, Google Sheets (via Service Account), dan PostgreSQL (via SQLAlchemy).
- **Unit test komprehensif** — setiap fungsi extract, transform, dan load diuji untuk skenario sukses maupun gagal menggunakan mocking (`unittest.mock`), dilengkapi pengukuran test coverage.

## Tech Stack
- **Bahasa:** Python
- **Scraping:** requests, BeautifulSoup4
- **Data processing:** pandas
- **Database:** SQLAlchemy, psycopg2-binary (PostgreSQL)
- **Google Sheets API:** google-auth, google-api-python-client
- **Testing:** unittest (mock), pytest-cov

## How It Works / Methodology

**1. Extract** (`utils/extract.py`)
- `fetching_content(url)` — mengambil HTML dari URL menggunakan `requests.Session`, dengan custom header User-Agent agar tidak ditolak server, dan penanganan error jika request gagal.
- `scrape_product(base_url, extract_product_data)` — mengiterasi seluruh halaman katalog (mendeteksi tombol "Next"), mengumpulkan seluruh produk hingga tidak ada halaman berikutnya.

**2. Transform** (`utils/transform.py`)
- `extract_product_data(div)` — mem-parsing satu blok HTML produk menjadi dictionary berisi Title, Price, Rating, Colors, Size, Gender.
- `clean_and_transform(data, exchange_rate=16000)` — membangun DataFrame, menambahkan kolom timestamp, menghapus baris tidak valid/duplikat/null, mengonversi tipe data setiap kolom sesuai kebutuhan (Price ke float dalam Rupiah, Rating ke float, Colors ke integer, Size & Gender ke string bersih).

**3. Load** (`utils/load.py`)
- `save_to_csv(df, filepath)` — menyimpan DataFrame ke file CSV.
- `save_to_gsheet(df, spreadsheet_id, range_name, credentials_file)` — mengautentikasi via Google Service Account, lalu menulis data ke Google Sheets.
- `store_to_postgre(df, db_url)` — menyimpan data ke tabel PostgreSQL menggunakan SQLAlchemy (mode append).

**4. Orkestrasi** (`main.py`)
Menjalankan ketiga tahapan secara berurutan: scrape → transform → simpan ke CSV → simpan ke Google Sheets → simpan ke PostgreSQL.

## Dataset
Bukan dataset statis — data diambil langsung (real-time scraping) dari situs katalog produk fashion [fashion-studio.dicoding.dev](https://fashion-studio.dicoding.dev/), sebuah situs latihan berisi data produk dummy (Title, Price, Rating, Colors, Size, Gender).

## Results / Output
Pipeline berhasil menghasilkan dataset bersih dengan kolom: `Title`, `Price` (Rupiah), `Rating` (float), `Colors` (integer), `Size`, `Gender`, `timestamp` — bebas dari nilai duplikat, null, maupun data tidak valid. Contoh hasil dapat dilihat pada `products.csv` di repo ini. Data yang sama juga berhasil disimpan ke Google Sheets dan PostgreSQL sebagai bukti pipeline penyimpanan multi-repository bekerja dengan baik.

## Installation
```bash
git clone https://github.com/septiisdayanna/project_akhir_pemda_septi_isdayanna.git
cd project_akhir_pemda_septi_isdayanna
pip install -r requirements.txt
```
Siapkan juga:
- `google-sheets-api.json` (Service Account credentials untuk Google Sheets API) — **jangan commit file ini**, sudah dikecualikan lewat `.gitignore`.
- Koneksi PostgreSQL lokal (atau sesuaikan `db_url` di `main.py`, sebaiknya lewat environment variable, bukan hardcode).

## Usage
Menjalankan pipeline ETL secara penuh:
```bash
python main.py
```

Menjalankan seluruh unit test:
```bash
python -m pytest tests
```

Mengecek test coverage:
```bash
python -m coverage run -m pytest tests
python -m coverage report
```

## Project Structure
```
project_akhir_pemda_septi_isdayanna/
├── tests/
│   ├── test_extract.py
│   ├── test_transform.py
│   └── test_load.py
├── utils/
│   ├── extract.py       # Scraping data dari website
│   ├── transform.py     # Pembersihan & transformasi data
│   └── load.py          # Penyimpanan ke CSV, Google Sheets, PostgreSQL
├── main.py              # Orkestrasi seluruh pipeline
├── requirements.txt
└── products.csv         # Contoh hasil output pipeline
```

## Limitations
- Koneksi database (`db_url`) saat ini di-hardcode langsung di `main.py`, termasuk kredensialnya — sebaiknya dipindahkan ke environment variable sebelum digunakan di luar lingkungan lokal/latihan.
- Sumber data adalah situs latihan (dummy catalog), bukan situs e-commerce produksi nyata, sehingga struktur HTML yang di-scrape relatif stabil dan sederhana dibanding situs nyata.
- Dependency `python-crontab` tercantum di `requirements.txt` namun belum digunakan di kode manapun — kemungkinan disiapkan untuk fitur scheduling yang belum diimplementasikan.

## Future Improvements
- Memindahkan seluruh kredensial (database, API key) ke environment variable atau file `.env` menggunakan `python-dotenv`.
- Memanfaatkan `python-crontab` yang sudah ada di dependency untuk menjadwalkan pipeline berjalan otomatis secara berkala.
- Mengganti `print()` dengan modul `logging` agar log lebih terstruktur dan mudah dipantau di lingkungan produksi.
- Menambahkan GitHub Actions untuk menjalankan unit test secara otomatis setiap ada perubahan kode (CI).

## Author
**Septi Isdayanna**
