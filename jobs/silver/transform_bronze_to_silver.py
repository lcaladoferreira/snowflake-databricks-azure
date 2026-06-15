from pyspark.sql.functions import col, upper, trim, to_timestamp
from src.utils.spark_utils import get_spark_session
from src.config.config import Config
from src.utils.logger import get_logger

logger = get_logger(__name__)

def transform_to_silver():
    spark = get_spark_session("SilverTransformation")

    # 1. Customers Transformation
    logger.info("Transforming customers to Silver...")
    cust_df = spark.read.format("delta").load(Config.get_storage_path("bronze", "customers"))
    cust_silver = cust_df.select(
        col("customer_id").cast("int"),
        trim(col("first_name")).alias("first_name"),
        trim(col("last_name")).alias("last_name"),
        upper(trim(col("email"))).alias("email"),
        to_timestamp(col("registration_date")).alias("registration_date"),
        col("_ingestion_timestamp")
    ).dropDuplicates(["customer_id"])
    cust_silver.write.format("delta").mode("overwrite").save(Config.get_storage_path("silver", "customers"))

    # 2. Products Transformation
    logger.info("Transforming products to Silver...")
    prod_df = spark.read.format("delta").load(Config.get_storage_path("bronze", "products"))
    prod_silver = prod_df.select(
        col("product_id").cast("int"),
        trim(col("product_name")).alias("product_name"),
        col("category"),
        col("price").cast("decimal(10,2)"),
        col("_ingestion_timestamp")
    ).dropDuplicates(["product_id"])
    prod_silver.write.format("delta").mode("overwrite").save(Config.get_storage_path("silver", "products"))

    # 3. Orders Transformation
    logger.info("Transforming orders to Silver...")
    orders_df = spark.read.format("delta").load(Config.get_storage_path("bronze", "orders"))
    orders_silver = orders_df.select(
        col("order_id").cast("int"),
        col("customer_id").cast("int"),
        to_timestamp(col("order_date")).alias("order_date"),
        upper(col("status")).alias("status"),
        col("_ingestion_timestamp")
    ).dropDuplicates(["order_id"])
    orders_silver.write.format("delta").mode("overwrite").save(Config.get_storage_path("silver", "orders"))

    # 4. Payments Transformation
    logger.info("Transforming payments to Silver...")
    payments_df = spark.read.format("delta").load(Config.get_storage_path("bronze", "payments"))
    payments_silver = payments_df.select(
        col("payment_id").cast("int"),
        col("order_id").cast("int"),
        col("payment_method"),
        col("payment_amount").cast("decimal(10,2)"),
        to_timestamp(col("payment_date")).alias("payment_date"),
        col("_ingestion_timestamp")
    ).dropDuplicates(["payment_id"])
    payments_silver.write.format("delta").mode("overwrite").save(Config.get_storage_path("silver", "payments"))

    # 5. Order Items Transformation
    logger.info("Transforming order_items to Silver...")
    items_df = spark.read.format("delta").load(Config.get_storage_path("bronze", "order_items"))
    items_silver = items_df.select(
        col("order_id").cast("int"),
        col("product_id").cast("int"),
        col("quantity").cast("int"),
        col("_ingestion_timestamp")
    )
    items_silver.write.format("delta").mode("overwrite").save(Config.get_storage_path("silver", "order_items"))

if __name__ == "__main__":
    transform_to_silver()
