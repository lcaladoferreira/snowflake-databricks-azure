import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_sample_data(output_dir="data/sample"):
    os.makedirs(output_dir, exist_ok=True)

    np.random.seed(42)
    num_customers = 100
    num_products = 20
    num_orders = 500

    # Customers
    customers = pd.DataFrame({
        "customer_id": range(1, num_customers + 1),
        "first_name": [f"FirstName{i}" for i in range(1, num_customers + 1)],
        "last_name": [f"LastName{i}" for i in range(1, num_customers + 1)],
        "email": [f"customer{i}@example.com" for i in range(1, num_customers + 1)],
        "registration_date": [datetime(2023, 1, 1) + timedelta(days=np.random.randint(0, 365)) for _ in range(num_customers)]
    })
    customers.to_csv(f"{output_dir}/customers.csv", index=False)

    # Products
    products = pd.DataFrame({
        "product_id": range(1, num_products + 1),
        "product_name": [f"Product {chr(65+i)}" for i in range(num_products)],
        "category": np.random.choice(["Electronics", "Clothing", "Home", "Garden"], num_products),
        "price": np.round(np.random.uniform(10.0, 500.0, num_products), 2)
    })
    products.to_csv(f"{output_dir}/products.csv", index=False)

    # Orders
    order_dates = [datetime(2024, 1, 1) + timedelta(days=np.random.randint(0, 90)) for _ in range(num_orders)]
    orders = pd.DataFrame({
        "order_id": range(1, num_orders + 1),
        "customer_id": np.random.randint(1, num_customers + 1, num_orders),
        "order_date": order_dates,
        "status": np.random.choice(["completed", "pending", "cancelled"], num_orders, p=[0.8, 0.1, 0.1])
    })
    orders.to_csv(f"{output_dir}/orders.csv", index=False)

    # Order Items (Transactions)
    order_items = []
    for order_id in range(1, num_orders + 1):
        num_items = np.random.randint(1, 5)
        for _ in range(num_items):
            product_id = np.random.randint(1, num_products + 1)
            quantity = np.random.randint(1, 10)
            order_items.append({
                "order_id": order_id,
                "product_id": product_id,
                "quantity": quantity
            })
    order_items_df = pd.DataFrame(order_items)
    order_items_df.to_csv(f"{output_dir}/order_items.csv", index=False)

    # Payments
    payments = pd.DataFrame({
        "payment_id": range(1, num_orders + 1),
        "order_id": range(1, num_orders + 1),
        "payment_method": np.random.choice(["credit_card", "paypal", "bank_transfer"], num_orders),
        "payment_amount": np.random.uniform(20.0, 1000.0, num_orders),
        "payment_date": order_dates
    })
    payments.to_csv(f"{output_dir}/payments.csv", index=False)

    print(f"Sample data generated in {output_dir}")

if __name__ == "__main__":
    generate_sample_data()
