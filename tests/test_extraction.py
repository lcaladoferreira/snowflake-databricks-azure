import unittest
from unittest.mock import MagicMock, patch

from src.extraction.snowflake_extractor import SnowflakeExtractor


class TestSnowflakeExtractor(unittest.TestCase):

    @patch("snowflake.connector.connect")
    def test_extract_table_success(self, mock_connect):
        # Setup mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock cursor description and fetchmany
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchmany.side_effect = [[(1, "test")], []]

        extractor = SnowflakeExtractor()

        # Mock metadata manager and write_to_storage
        extractor.metadata_mgr = MagicMock()
        extractor._write_to_storage = MagicMock(return_value="/tmp/test.parquet")

        # Run extraction
        extractor.extract_table("CUSTOMERS")

        # Verifications
        mock_cursor.execute.assert_called_once()
        extractor.metadata_mgr.log_extraction.assert_called()
        self.assertEqual(
            extractor.metadata_mgr.log_extraction.call_args[1]["status"], "SUCCESS"
        )

    @patch("snowflake.connector.connect")
    def test_extract_table_incremental(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.description = [("id",), ("updated_at",)]
        mock_cursor.fetchmany.side_effect = [[(1, "2024-01-01")], []]

        extractor = SnowflakeExtractor()
        extractor.metadata_mgr = MagicMock()
        extractor._write_to_storage = MagicMock()

        # Mock getting last watermark
        with patch.object(extractor.metadata_mgr, "get_last_watermark", return_value="2023-01-01"):
            extractor.extract_table("ORDERS", incremental_col="updated_at")

        # Verify query contains WHERE clause and params are correct
        query = mock_cursor.execute.call_args[0][0]
        params = mock_cursor.execute.call_args[0][1]
        self.assertIn("WHERE updated_at > %s", query)
        self.assertEqual(params, ("2023-01-01",))

    @patch("snowflake.connector.connect")
    def test_extract_table_failure(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Simulate exception during execute
        mock_cursor.execute.side_effect = Exception("Snowflake error")

        extractor = SnowflakeExtractor()
        extractor.metadata_mgr = MagicMock()

        with self.assertRaises(Exception):
            extractor.extract_table("CUSTOMERS")

        # Verify failure was logged
        extractor.metadata_mgr.log_extraction.assert_called()
        self.assertEqual(
            extractor.metadata_mgr.log_extraction.call_args[1]["status"], "FAILED"
        )


if __name__ == "__main__":
    unittest.main()
