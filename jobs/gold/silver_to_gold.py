from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, count as _count, avg as _avg, date_format
from src.config.config import Config

logger = Config.get_logger(__name__)

def create_gold_marts(spark: SparkSession):
    """Generates analytical Star Schema and Data Marts in Gold."""

    logger.info("Generating Gold layer analytical tables...")

    silver_base = Config.get_storage_path("silver")
    gold_base = Config.get_storage_path("gold")

    # Load Silver
    orders = spark.read.format("delta").load(f"{silver_base}/orders")
    items = spark.read.format("delta").load(f"{silver_base}/order_items")
    payments = spark.read.format("delta").load(f"{silver_base}/payments")
    customers = spark.read.format("delta").load(f"{silver_base}/customers")

    # 1. Fact Orders (Denormalized for performance)
    fact_orders = (orders.alias("o")
                   .join(items.alias("i"), "order_id")
                   .join(payments.alias("p"), "order_id")
                   .select("o.*", "i.product_id", "i.quantity", "p.payment_amount", "p.payment_method"))

    (fact_orders.write.format("delta")
     .mode("overwrite")
     .option("overwriteSchema", "true")
     .save(f"{gold_base}/fact_orders"))

    # 2. Mart: Daily Sales
    daily_sales = (fact_orders.groupBy(date_format("order_date", "yyyy-MM-dd").alias("order_day"))
                   .agg(_sum("payment_amount").alias("daily_revenue"),
                        _count("order_id").alias("order_count"))
                   .orderBy("order_day"))

    (daily_sales.write.format("delta")
     .mode("overwrite")
     .save(f"{gold_base}/mart_daily_sales"))

    # Optimization (Z-Order) - Placeholder for production performance
    # spark.sql(f"OPTIMIZE delta.`{gold_base}/fact_orders` ZORDER BY (customer_id)")

    logger.info("Gold marts created successfully.")

if __name__ == "__main__":
    from src.utils.spark_utils import get_spark_session
    s = get_spark_session("GoldProcessing")
    create_gold_marts(s)
