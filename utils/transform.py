import pandas as pd # untuk manipulasi data
from datetime import datetime # untuk mendapatkan waktu saat ini
import re # untuk ekspresi reguler

def extract_product_data(div):
    """Fungsi ini digunakan untuk mengambil data produk dari elemen div yang diberikan."""

    # Judul produk
    title_element = div.find('h3', class_='product-title')
    title = title_element.text.strip() if title_element else "Unknown Product"

    # Harga produk
    price_container = div.find('div', class_='price-container')
    price_element = price_container.find('span', class_='price') if price_container else None
    price = price_element.text.strip() if price_element else "Price Unavailable"

    # Detail produk (rating, colors, size, gender)
    product_info_elements = div.find_all('p', style="font-size: 14px; color: #777;")
    rating = "Not available"
    colors = "Not available"
    size = "Not available"
    gender = "Not available"

    for info in product_info_elements:
        text = info.text.strip()
        if "Rating" in text and ":" in text:
            rating = text.split(":")[1].strip()
        elif "Color" in text:
            match = re.search(r'(\d+)', text)
            if match:
                colors = match.group(1)
        elif "Size" in text and ":" in text:
            size = text.split(":")[1].strip()
        elif "Gender" in text and ":" in text:
            gender = text.split(":")[1].strip()

    return {
        "Title": title,
        "Price": price,
        "Rating": rating,
        "Colors": colors,
        "Size": size,
        "Gender": gender
    }

def clean_and_transform(data: list, extraction_time=None,  exchange_rate=16000):
    """ Fungsi untuk membersihkan dan mentransformasi data hasil scraping."""
    try:
        df = pd.DataFrame(data)

        # Tambahkan kolom timestamp
        extraction_time = pd.to_datetime(extraction_time or datetime.now())
        df["timestamp"] = extraction_time

        # Pola data yang dianggap tidak valid
        dirty_patterns = {
            "Title": ["Unknown Product"],
            "Rating": ["Invalid Rating / 5", "Not Rated", "Not available", None],
            "Price": ["Price Unavailable", "Not available", None],
        }

        # Buat invalid_mask secara dinamis dari dirty_patterns
        invalid_mask = pd.Series(False, index=df.index)
        for col, patterns in dirty_patterns.items():
            if col in df.columns:
                invalid_mask |= df[col].isin(patterns)

        print(f"Baris tidak valid yang dihapus: {invalid_mask.sum()}")
        df = df[~invalid_mask].copy()

        # Bersihkan kolom Price
        df['Price'] = (
            pd.to_numeric(
                df['Price']
                .str.replace(r'[^\d.]', '', regex=True),
                errors='coerce'  # ubah error jadi NaN
            ) * exchange_rate 
        )

        # Bersihkan kolom Rating
        df["Rating"] = (
            df["Rating"]
            .str.extract(r"(\d+\.\d+|\d+)")[0]
            .astype(float)
        )     

        # Bersihkan kolom Colors
        df["Colors"] = (
            pd.to_numeric(
                df["Colors"]
                .astype(str)
                .str.extract(r"(\d+)")[0], 
                errors='coerce' # ubah error jadi NaN
            ) 
            .astype('Int64')
        )

        # Bersihkan kolom Size  
        df["Size"] = (
            df["Size"]
            .astype(str)
            .str.strip()
            .str.replace(r"^Size:\s*", "", regex=True)
        )

        # Bersihkan kolom Gender
        df["Gender"] = (
            df["Gender"]
            .astype(str)
            .str.strip()
            .str.replace(r"^Gender:\s*", "", regex=True)
        )

        # Tampilkan jumlah null sebelum drop
        print("Jumlah nilai null per kolom sebelum dropna():")
        print(df.isnull().sum())

        # Drop nilai null
        before = len(df)
        df.dropna(inplace=True)
        print(f"Dihapus {before - len(df)} baris karena null.")

        # Drop duplikat
        df.drop_duplicates(inplace=True)

        # Ubah tipe data akhir
        df = df.astype({
            "Title": "object",
            "Price": "float64",
            "Rating": "float64",
            "Colors": "Int64",
            "Size": "object",
            "Gender": "object",
            "timestamp": "object"
        })

        return df

    except Exception as e:
        print(f"Error saat proses transformasi: {e}")
        return pd.DataFrame()  # Kembalikan DataFrame kosong jika error

