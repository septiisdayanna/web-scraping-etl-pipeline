import unittest
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from utils.transform import extract_product_data, clean_and_transform

class TestTransform(unittest.TestCase):
    """Test suite untuk modul transform.py"""
    
    def setUp(self):
        """Setup data uji yang akan digunakan di beberapa test"""
        self.valid_html = """
        <div class="product-details">
            <h3 class="product-title">Test Product</h3>
            <div class="price-container">
                <span class="price">$100.00</span>
            </div>
            <p style="font-size: 14px; color: #777;">Rating: 4.5 / 5</p>
            <p style="font-size: 14px; color: #777;">Color: 3 Colors</p>
            <p style="font-size: 14px; color: #777;">Size: M</p>
            <p style="font-size: 14px; color: #777;">Gender: Men</p>
        </div>
        """
        
        self.empty_html = "<div class='product-details'></div>"
        
        self.valid_data = [
            {
                "Title": "Product 1",
                "Price": "$10.99",
                "Rating": "4.5 / 5",
                "Colors": "3 Colors",
                "Size": "Size: M",
                "Gender": "Gender: Men"
            },
            {
                "Title": "Product 2",
                "Price": "$20.50",
                "Rating": "3.8",
                "Colors": "2",
                "Size": "L",
                "Gender": "Women"
            }
        ]
        
        self.extraction_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.exchange_rate = 16000

    def test_extract_product_data_with_valid_html(self):
        """Test ekstraksi data dari HTML yang valid"""
        soup = BeautifulSoup(self.valid_html, 'html.parser')
        div = soup.find('div', class_='product-details')
        result = extract_product_data(div)
        
        expected = {
            "Title": "Test Product",
            "Price": "$100.00",
            "Rating": "4.5 / 5",
            "Colors": "3",
            "Size": "M",
            "Gender": "Men"
        }
        self.assertEqual(result, expected)

    def test_extract_product_data_with_empty_html(self):
        """Test ekstraksi data dari HTML yang tidak lengkap"""
        soup = BeautifulSoup(self.empty_html, 'html.parser')
        div = soup.find('div', class_='product-details')
        result = extract_product_data(div)
        
        expected = {
            "Title": "Unknown Product",
            "Price": "Price Unavailable",
            "Rating": "Not available",
            "Colors": "Not available",
            "Size": "Not available",
            "Gender": "Not available"
        }
        self.assertEqual(result, expected)

    def test_clean_and_transform_with_valid_data(self):
        """Test transformasi data yang valid"""
        result = clean_and_transform(
            self.valid_data, 
            self.extraction_time, 
            self.exchange_rate
        )

        # Verifikasi hasil dasar
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        
        # Verifikasi konversi harga
        expected_prices = [10.99 * 16000, 20.50 * 16000]
        self.assertTrue(all(result['Price'].values == expected_prices))
        
        # Verifikasi konversi rating
        expected_ratings = [4.5, 3.8]
        self.assertTrue(all(result['Rating'].values == expected_ratings))
        
        # Verifikasi cleaning text
        self.assertEqual(result['Size'].iloc[0], 'M')
        self.assertEqual(result['Gender'].iloc[0], 'Men')
        self.assertEqual(result['Colors'].iloc[0], 3)
        
        # Verifikasi timestamp
        self.assertEqual(
            result['timestamp'].iloc[0].floor('s'), 
            pd.to_datetime(self.extraction_time)
        )
        
        # Verifikasi tipe data
        self.assertTrue(pd.api.types.is_float_dtype(result['Price']))
        self.assertTrue(pd.api.types.is_float_dtype(result['Rating']))
        self.assertTrue(pd.api.types.is_integer_dtype(result['Colors']))
        self.assertTrue(pd.api.types.is_string_dtype(result['Size']))

    def test_clean_and_transform_with_invalid_data(self):
        """Test transformasi dengan data tidak valid"""
        test_data = self.valid_data.copy()
        test_data.append({
            "Title": "Unknown Product",
            "Price": "Price Unavailable",
            "Rating": "Not Rated",
            "Colors": "Not available",
            "Size": "Not available",
            "Gender": "Not available"
        })
        
        result = clean_and_transform(test_data, exchange_rate=self.exchange_rate)
        
        # Hanya data valid yang seharusnya tersisa
        self.assertEqual(len(result), len(self.valid_data))
        self.assertTrue(all(result['Title'] != "Unknown Product"))

    def test_clean_and_transform_with_missing_values(self):
        """Test transformasi dengan data yang memiliki nilai kosong"""
        test_data = self.valid_data.copy()
        test_data.append({
            "Title": "Product 3",
            "Price": None,
            "Rating": "4.2",
            "Colors": "1",
            "Size": "XL",
            "Gender": "Women"
        })
        
        result = clean_and_transform(test_data, exchange_rate=self.exchange_rate)
        
        # Baris dengan nilai kosong seharusnya dihapus
        self.assertEqual(len(result), len(self.valid_data))
        self.assertTrue(all(result['Price'].notna()))

    def test_clean_and_transform_with_duplicates(self):
        """Test penghapusan data duplikat"""
        test_data = self.valid_data.copy()
        test_data.append(self.valid_data[0])  # Tambahkan duplikat
        
        result = clean_and_transform(test_data, exchange_rate=self.exchange_rate)
        
        # Duplikat seharusnya dihapus
        self.assertEqual(len(result), len(self.valid_data))
        self.assertEqual(result.duplicated().sum(), 0)

    def test_clean_and_transform_with_empty_input(self):
        """Test dengan input kosong"""
        result = clean_and_transform([], exchange_rate=self.exchange_rate)
        self.assertTrue(result.empty)

    def test_clean_and_transform_error_handling(self):
        """Test penanganan error"""
        # Input tidak valid untuk memicu exception
        result = clean_and_transform("bukan list", exchange_rate=self.exchange_rate)
        self.assertTrue(result.empty)

if __name__ == '__main__':
    unittest.main()