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


if __name__ == "__main__":
    unittest.main()
