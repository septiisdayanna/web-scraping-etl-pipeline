import unittest
import requests
from unittest.mock import patch, MagicMock
from utils.extract import fetching_content, scrape_product

class TestExtract(unittest.TestCase):

    @patch('requests.Session')
    def test_fetching_content_success(self, mock_session):
        """Uji pengambilan konten HTML yang berhasil."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b"<html><body>Data</body></html>"
        mock_session.return_value.get.return_value = mock_response

        url = "http://example.com"
        content = fetching_content(url)

        self.assertEqual(content, b"<html><body>Data</body></html>")
        mock_session.return_value.get.assert_called_once_with(url, headers=unittest.mock.ANY)
        mock_response.raise_for_status.assert_called_once()

    @patch('requests.Session')
    def test_fetching_content_failure(self, mock_session):
        """Uji ketika request HTTP gagal."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.RequestException("HTTP Error")
        mock_session.return_value.get.return_value = mock_response

        url = "http://example.com/error"
        content = fetching_content(url)

        self.assertIsNone(content)
        mock_session.return_value.get.assert_called_once_with(url, headers=unittest.mock.ANY)
        mock_response.raise_for_status.assert_called_once()

    @patch('utils.extract.fetching_content')
    @patch('time.sleep', return_value=None)
    def test_scrape_product_single_page(self, mock_sleep, mock_fetching_content):
        """Uji fungsi scrape_product untuk satu halaman."""
        mock_html = """
        <html><body>
            <div class="product-details">
                <h3 class="product-title">Product 1</h3>
                <div class="price-container"><span class="price">$50</span></div>
                <p style="font-size: 14px; color: #777;">Rating: 4.0 / 5</p>
                <p style="font-size: 14px; color: #777;">Colors: 2 Colors</p>
                <p style="font-size: 14px; color: #777;">Size: S</p>
                <p style="font-size: 14px; color: #777;">Gender: Women</p>
            </div>
        </body></html>
        """
        mock_fetching_content.return_value = mock_html

        def mock_extract(div):
            return {
                "Title": div.find('h3').text.strip(),
                "Price": div.find('span', class_='price').text.strip(),
                "Rating": "4.0",
                "Colors": "2 Colors",
                "Size": "S",
                "Gender": "Women"
            }

        base_url = ["http://example.com/"]
        extracted_data = scrape_product(base_url, mock_extract)

        self.assertEqual(len(extracted_data), 1)
        self.assertEqual(extracted_data[0]["Title"], "Product 1")
        self.assertEqual(extracted_data[0]["Price"], "$50")

    @patch('utils.extract.fetching_content')
    @patch('time.sleep', return_value=None)
    def test_scrape_product_multiple_pages(self, mock_sleep, mock_fetching_content):
        """Uji fungsi scrape_product ketika ada beberapa halaman (Next)."""
        mock_content_page1 = """
        <html><body>
            <div class="product-details">
                <h3 class="product-title">Product 1</h3>
                <div class="price-container"><span class="price">$50</span></div>
                <p style="font-size: 14px; color: #777;">Rating: 4.0 / 5</p>
                <p style="font-size: 14px; color: #777;">Colors: 2 Colors</p>
                <p style="font-size: 14px; color: #777;">Size: S</p>
                <p style="font-size: 14px; color: #777;">Gender: Women</p>
            </div>
            <li class="page-item next"><a class="page-link" href="#">Next</a></li>
        </body></html>
        """
        mock_content_page2 = """
        <html><body>
            <div class="product-details">
                <h3 class="product-title">Product 2</h3>
                <div class="price-container"><span class="price">$75</span></div>
                <p style="font-size: 14px; color: #777;">Rating: 4.2 / 5</p>
                <p style="font-size: 14px; color: #777;">Colors: 4 Colors</p>
                <p style="font-size: 14px; color: #777;">Size: L</p>
                <p style="font-size: 14px; color: #777;">Gender: Men</p>
            </div>
        </body></html>
        """
        mock_fetching_content.side_effect = [mock_content_page1, mock_content_page2, None]

        def mock_extract(div):
            return {
                "Title": div.find('h3').text.strip(),
                "Price": div.find('span', class_='price').text.strip(),
                "Rating": div.find_all('p')[0].text.split(":")[1].strip().split("/")[0],
                "Colors": div.find_all('p')[1].text.split(":")[1].strip(),
                "Size": div.find_all('p')[2].text.split(":")[1].strip(),
                "Gender": div.find_all('p')[3].text.split(":")[1].strip()
            }

        base_url = ["http://example.com/", "http://example.com/page={}"]
        extracted_data = scrape_product(base_url, mock_extract)

        self.assertEqual(len(extracted_data), 2)
        self.assertEqual(extracted_data[0]['Title'], 'Product 1')
        self.assertEqual(extracted_data[1]['Title'], 'Product 2')
        self.assertEqual(mock_fetching_content.call_count, 2)

if __name__ == '__main__':
    unittest.main()
