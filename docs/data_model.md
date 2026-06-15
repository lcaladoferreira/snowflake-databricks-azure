# Data Model: Medallion Architecture

This project implements a Retail/E-commerce data model.

## Silver Layer (Conformed Entities)
- `customers`: Standardized customer profiles.
- `products`: Product catalog with clean attributes.
- `orders`: Transaction headers.
- `order_items`: Granular line items.
- `payments`: Payment transaction records.

## Gold Layer (Star Schema)

### Dimensions
- `dim_customers`: SCD Type 1 or Type 2 customer info.
- `dim_products`: Product details.
- `dim_date`: Standardized date dimension for time-series analysis.

### Facts
- `fact_orders`: Central fact table for sales.
- `fact_payments`: Payment success and revenue tracking.

### Metrics
- `total_revenue`: SUM(payment_amount) where status = 'success'.
- `order_count`: COUNT(DISTINCT order_id).
- `avg_order_value`: total_revenue / order_count.
