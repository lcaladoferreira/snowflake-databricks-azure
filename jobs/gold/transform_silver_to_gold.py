from pyspark.sql.functions import col, sum as _sum, count as _count, avg as _avg, date_format
from src.utils.spark_utils import get_spark_session
from src.config.config import Config
from src.utils.logger import get_logger

logger = get_logger(__name__)

def transform_to_gold():
    spark = get_spark_session("GoldTransformation")

    # Load Silver tables
    cust_s = spark.read.format("delta").load(Config.get_storage_path("silver", "customers"))
    prod_s = spark.read.format("delta").load(Config.get_storage_path("silver", "products"))
    orders_s = spark.read.format("delta").load(Config.get_storage_path("silver", "orders"))
    payments_s = spark.read.format("delta").load(Config.get_storage_path("silver", "payments"))
    items_s = spark.read.format("delta").load(Config.get_storage_path("silver", "order_items"))

    # --- Dimensions ---
    logger.info("Creating Gold Dimensions...")
    dim_customers = cust_s.select("customer_id", "first_name", "last_name", "email", "registration_date")
    dim_customers.write.format("delta").mode("overwrite").save(Config.get_storage_path("gold", "dim_customers"))

    dim_products = prod_s.select("product_id", "product_name", "category", "price")
    dim_products.write.format("delta").mode("overwrite").save(Config.get_storage_path("gold", "dim_products"))

    # --- Facts ---
    logger.info("Creating Gold Facts...")
    fact_orders = orders_s.join(items_s, "order_id", "left") \
                         .join(payments_s.select("order_id", "payment_amount", "payment_method"), "order_id", "left") \
                         .select(
                             "order_id", "customer_id", "product_id", "order_date",
                             "status", "quantity", "payment_amount"
                         )
    fact_orders.write.format("delta").mode("overwrite").save(Config.get_storage_path("gold", "fact_orders"))

    # --- Analytical Data Mart (Metrics) ---
    logger.info("Creating Analytical Metrics...")
    sales_metrics = fact_orders.groupBy(date_format("order_date", "yyyy-MM").alias("month")) \
                               .agg(
                                   _sum("payment_amount").alias("total_revenue"),
                                   _count("order_id").alias("total_orders"),
                                   _avg("payment_amount").alias("avg_order_value")
                               ).orderBy("month")

    sales_metrics.write.format("delta").mode("overwrite").save(Config.get_storage_path("gold", "mart_sales_monthly"))
    logger.info("Gold layer transformation complete.")

if __name__ == "__main__":
    transform_to_gold()
