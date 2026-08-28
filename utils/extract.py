import time # Digunakan menerapkan throttling untuk menambahkan delay 2 detik pada setiap permintaan HTTP.
import requests # Digunakan untuk melakukan HTTP requests ke website yang akan diambil datanya.
from bs4 import BeautifulSoup # Digunakan untuk web scraping.

# Mendefinisikan user-agent agar permintaan tidak ditolak oleh server
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    )
}

def fetching_content(url):
    """Mengambil konten HTML dari URL yang diberikan."""
    session = requests.Session()
    try:
        response = session.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Terjadi kesalahan saat request {url}: {e}")
        return None

def scrape_product(base_url, extract_product_data, start_page=1, delay=2):
    """Fungsi utama untuk mengambil keseluruhan data, mulai dari requests hingga menyimpannya dalam variabel data."""
    data = []
    page_number = start_page

    while True:
        url = base_url[0] if page_number == 1 else base_url[1].format(page_number)
        print(f"Scraping halaman: {url}")

        content = fetching_content(url)
        if content:
            soup = BeautifulSoup(content, "html.parser")
            divs = soup.find_all('div', class_='product-details')

            for div in divs:
                product = extract_product_data(div)
                data.append(product)

            next_button = soup.find('li', class_='page-item next')
            if next_button:
                page_number += 1
                time.sleep(delay)# Delay sebelum halaman berikutnya
            else:
                break # Berhenti jika sudah tidak ada next button
        else:
            break # Berhenti jika ada kesalahan

    return data
