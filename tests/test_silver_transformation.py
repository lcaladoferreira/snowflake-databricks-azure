import unittest
from unittest.mock import MagicMock, patch
from jobs.silver.bronze_to_silver import SilverTransformer
from tests.pyspark_test_base import PySparkTestCase


class TestSilverTransformation(PySparkTestCase):
    def setUp(self):
        self.transformer = SilverTransformer(self.spark)

    @patch("src.config.config.Config.get_storage_path")
    def test_transform_customers_logic(self, mock_path):
        # Create small test data
        data = [
            (1, "John", "Doe", "john@example.com", "2023-01-01", "2023-06-15 10:00:00")
        ]
        schema = [
            "customer_id",
            "first_name",
            "last_name",
            "email",
            "registration_date",
            "_ingestion_timestamp",
        ]
        test_df = self.spark.createDataFrame(data, schema)

        # Use real paths for the test
        bronze_path = "data/test_bronze/customers"
        test_df.write.format("delta").mode("overwrite").save(bronze_path)

        mock_path.side_effect = lambda layer, table: (
            bronze_path if layer == "bronze" else f"data/test_{layer}/{table}"
        )

        # Execution
        # We mock _upsert to avoid real MERGE complexity in a small unit test
        self.transformer._upsert = MagicMock()
        self.transformer.transform_customers()

        # Verify
        self.transformer._upsert.assert_called_once()
        args, _ = self.transformer._upsert.call_args
        result_df = args[0]
        self.assertEqual(result_df.count(), 1)
        self.assertTrue("email" in result_df.columns)


if __name__ == "__main__":
    unittest.main()
