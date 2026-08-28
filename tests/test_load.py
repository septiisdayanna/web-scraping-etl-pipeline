import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import io

from utils.load import save_to_csv, save_to_gsheet, store_to_postgre

class TestLoadFunctions(unittest.TestCase):

    def setUp(self):
        """Set up test data dan parameters."""
        self.test_df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        self.filepath = "test.csv"
        self.spreadsheet_id = "spreadsheet_id"
        self.range_name = "Sheet1!A1"
        self.credentials_file = "credentials.json"
        self.db_url = "postgresql://user:pass@localhost:5432/testdb"

    # ============ TEST SAVE TO CSV ============
    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('pandas.DataFrame.to_csv')
    def test_save_to_csv_success(self, mock_to_csv, mock_stdout):
        """Test fungsi save_to_csv untuk menyimpan DataFrame ke CSV."""
        save_to_csv(self.test_df, self.filepath)
        mock_to_csv.assert_called_once_with(self.filepath, index=False)
        self.assertIn(f"Data berhasil disimpan ke {self.filepath}", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('pandas.DataFrame.to_csv', side_effect=IOError("Disk full"))
    def test_save_to_csv_failure(self, mock_to_csv, mock_stdout):
        """Test fungsi save_to_csv untuk menangani kesalahan saat menyimpan CSV."""
        save_to_csv(self.test_df, self.filepath)
        self.assertIn("Gagal menyimpan data: Disk full", mock_stdout.getvalue())

    # ============ TEST SAVE TO GOOGLE SHEETS ============
    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('utils.load.build')
    @patch('google.oauth2.service_account.Credentials.from_service_account_file')
    def test_save_to_gsheet_success(self, mock_from_file, mock_build, mock_stdout):
        """Test fungsi save_to_gsheet untuk menyimpan DataFrame ke Google Sheets."""
        mock_creds = MagicMock()
        mock_from_file.return_value = mock_creds
        mock_service = MagicMock()
        mock_values = MagicMock()
        mock_update = MagicMock()
        mock_update.execute.return_value = {'updatedCells': 4}
        mock_values.update.return_value = mock_update
        mock_service.spreadsheets.return_value.values.return_value = mock_values
        mock_build.return_value = mock_service

        result = save_to_gsheet(
            df=self.test_df,
            spreadsheet_id=self.spreadsheet_id,
            range_name=self.range_name,
            credentials_file=self.credentials_file
        )

        self.assertTrue(result is None)  # karena fungsi tidak mengembalikan apapun
        mock_from_file.assert_called_once()
        mock_build.assert_called_once_with('sheets', 'v4', credentials=mock_creds)
        mock_values.update.assert_called_once()
        self.assertIn("Data berhasil ditambahkan ke Google Sheets!", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('google.oauth2.service_account.Credentials.from_service_account_file', side_effect=Exception("Invalid credentials"))
    def test_save_to_gsheet_failure(self, mock_from_file, mock_stdout):
        """Test fungsi save_to_gsheet untuk menangani kesalahan saat menyimpan ke Google Sheets."""
        result = save_to_gsheet(
            df=self.test_df,
            spreadsheet_id=self.spreadsheet_id,
            range_name=self.range_name,
            credentials_file="invalid.json"
        )
        self.assertTrue(result is None) 
        self.assertIn("Gagal menyimpan data ke Google Sheets: Invalid credentials", mock_stdout.getvalue())

    # ============ TEST SAVE TO POSTGRE ============
    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('pandas.DataFrame.to_sql')
    @patch('utils.load.create_engine')
    def test_store_to_postgre_success(self, mock_create_engine, mock_to_sql, mock_stdout):
        """Test fungsi store_to_postgre untuk menyimpan DataFrame ke PostgreSQL."""
        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_create_engine.return_value = mock_engine

        store_to_postgre(self.test_df, self.db_url)

        mock_create_engine.assert_called_once_with(self.db_url)
        mock_to_sql.assert_called_once_with('productstoscrape', con=mock_conn, if_exists='append', index=False)
        self.assertIn("Data berhasil ditambahkan ke PostgreSQL!", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('utils.load.create_engine', side_effect=Exception("DB error"))
    def test_store_to_postgre_failure(self, mock_create_engine, mock_stdout):
        """Test fungsi store_to_postgre untuk menangani kesalahan saat menyimpan ke PostgreSQL."""
        store_to_postgre(self.test_df, self.db_url)
        self.assertIn("Terjadi kesalahan saat menyimpan data ke PostgreSQL: DB error", mock_stdout.getvalue())

if __name__ == '__main__':
    unittest.main()
