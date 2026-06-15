from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count as _count, date_format, sum as _sum

from src.config.config import Config

logger = Config.get_logger(__name__)


def create_gold_marts(spark: SparkSession) -> None:
    """Creates a high-performance Star Schema and Analytical Data Marts."""

    silver_path = Config.get_storage_path("silver")
    gold_path = Config.get_storage_path("gold")

    # Load Source Tables
    customers = spark.read.format("delta").load(f"{silver_path}/customers")
    products = spark.read.format("delta").load(f"{silver_path}/products")
    orders = spark.read.format("delta").load(f"{silver_path}/orders")
    payments = spark.read.format("delta").load(f"{silver_path}/payments")
    items = spark.read.format("delta").load(f"{silver_path}/order_items")

    # 1. Dimensions
    customers.select(
        "customer_id", "first_name", "last_name", "email", "registration_date"
    ).write.format("delta").mode("overwrite").save(f"{gold_path}/dim_customers")

    products.select("product_id", "product_name", "category", "price").write.format(
        "delta"
    ).mode("overwrite").save(f"{gold_path}/dim_products")

    # 2. Fact Orders
    fact_orders = (
        orders.alias("o")
        .join(items.alias("i"), "order_id")
        .join(payments.alias("p"), "order_id")
        .select(
            col("o.order_id"),
            col("o.customer_id"),
            col("i.product_id"),
            col("o.order_date"),
            col("o.status"),
            col("i.quantity"),
            col("p.payment_amount"),
            col("p.payment_method"),
        )
    )
    fact_orders.write.format("delta").mode("overwrite").save(f"{gold_path}/fact_orders")

    # 3. Analytical Marts
    # Daily Sales
    daily_sales = (
        fact_orders.groupBy(date_format("order_date", "yyyy-MM-dd").alias("sales_date"))
        .agg(
            _sum("payment_amount").alias("revenue"),
            _count("order_id").alias("order_count"),
        )
        .orderBy("sales_date")
    )
    daily_sales.write.format("delta").mode("overwrite").save(
        f"{gold_path}/mart_sales_daily"
    )

    # Customer Lifetime Value
    clv_mart = (
        fact_orders.groupBy("customer_id")
        .agg(
            _sum("payment_amount").alias("lifetime_value"),
            _count("order_id").alias("total_orders"),
        )
        .orderBy(col("lifetime_value").desc())
    )
    clv_mart.write.format("delta").mode("overwrite").save(f"{gold_path}/mart_clv")

    # Optimization Step (Production only)
    if Config.EXECUTION_MODE != "demo":
        logger.info("Applying Z-Order optimization to Gold Fact table.")
        spark.sql(
            f"OPTIMIZE delta.`{gold_path}/fact_orders` ZORDER BY (customer_id, order_date)"
        )

    logger.info("Gold layer Star Schema and Data Marts successfully updated.")
