import unittest
from unittest.mock import patch, MagicMock

from jobs.gold.silver_to_gold import create_gold_marts
from tests.pyspark_test_base import PySparkTestCase


class TestGoldProcessing(PySparkTestCase):
    def test_create_gold_marts_creates_fact_orders(self):
        # Create Mock Silver Data
        orders_data = [(1, 101, "2024-01-01", "COMPLETED")]
        orders_schema = ["order_id", "customer_id", "order_date", "status"]
        orders_df = self.spark.createDataFrame(orders_data, orders_schema)

        items_data = [(1, 201, 2)]
        items_schema = ["order_id", "product_id", "quantity"]
        items_df = self.spark.createDataFrame(items_data, items_schema)

        payments_data = [(1, 100.0, "CREDIT_CARD")]
        payments_schema = ["order_id", "payment_amount", "payment_method"]
        payments_df = self.spark.createDataFrame(payments_data, payments_schema)

        customers_data = [(101, "JOHN", "DOE", "JOHN@EXAMPLE.COM", "2023-01-01")]
        customers_schema = [
            "customer_id",
            "first_name",
            "last_name",
            "email",
            "registration_date",
        ]
        customers_df = self.spark.createDataFrame(customers_data, customers_schema)

        # Create physical delta tables for Spark to read
        import os
        import shutil
        silver_base = "data/test_silver_gold"
        os.makedirs(silver_base, exist_ok=True)

        orders_df.write.format("delta").mode("overwrite").save(f"{silver_base}/orders")
        items_df.write.format("delta").mode("overwrite").save(f"{silver_base}/order_items")
        payments_df.write.format("delta").mode("overwrite").save(f"{silver_base}/payments")
        customers_df.write.format("delta").mode("overwrite").save(f"{silver_base}/customers")
        # Mock products as customers for simplicity
        customers_df.select("customer_id", "first_name", "last_name", "registration_date").toDF("product_id", "product_name", "category", "price").write.format("delta").mode("overwrite").save(f"{silver_base}/products")

        gold_base = "data/test_gold_output"
        os.makedirs(gold_base, exist_ok=True)

        with patch("src.config.config.Config.get_storage_path") as mock_path:
            mock_path.side_effect = lambda layer, table=None: (
                silver_base if layer == "silver" else gold_base
            )
            create_gold_marts(self.spark)

        # Verify gold tables were created
        self.assertTrue(os.path.exists(f"{gold_base}/fact_orders"))
        self.assertTrue(os.path.exists(f"{gold_base}/dim_customers"))

        # Verify columns
        fact_orders = self.spark.read.format("delta").load(f"{gold_base}/fact_orders")
        expected_cols = {"order_id", "customer_id", "payment_amount", "order_date", "payment_method"}
        self.assertTrue(expected_cols.issubset(set(fact_orders.columns)))

        # Cleanup
        shutil.rmtree(silver_base)
        shutil.rmtree(gold_base)

    def test_fact_orders_no_duplicate_order_ids(self):
        orders_data = [(1, 101, "2024-01-01", "COMPLETED")]
        orders_schema = ["order_id", "customer_id", "order_date", "status"]
        orders_df = self.spark.createDataFrame(orders_data, orders_schema)

        items_data = [(1, 201, 2)]
        items_schema = ["order_id", "product_id", "quantity"]
        items_df = self.spark.createDataFrame(items_data, items_schema)

        payments_data = [(1, 100.0, "CREDIT_CARD")]
        payments_schema = ["order_id", "payment_amount", "payment_method"]
        payments_df = self.spark.createDataFrame(payments_data, payments_schema)

        from pyspark.sql.functions import col
        fact_orders = (
            orders_df.alias("o")
            .join(items_df.alias("i"), "order_id")
            .join(payments_df.alias("p"), "order_id")
            .select(col("o.order_id"))
        )

        duplicate_count = fact_orders.groupBy("order_id").count().filter("count > 1").count()
        self.assertEqual(duplicate_count, 0)

    def test_dim_customers_email_is_uppercase(self):
        silver_customers_data = [(101, "JOHN", "DOE", "JOHN@EXAMPLE.COM", "2023-01-01")]
        customers_schema = [
            "customer_id",
            "first_name",
            "last_name",
            "email",
            "registration_date",
        ]
        silver_customers_df = self.spark.createDataFrame(silver_customers_data, customers_schema)

        dim_customers = silver_customers_df.select("email")

        emails = [row.email for row in dim_customers.collect()]
        for email in emails:
            self.assertEqual(email, email.upper())


if __name__ == "__main__":
    unittest.main()
