from pathlib import Path
import pandas as pd
import sqlite3

orders = pd.read_csv("olist_orders_dataset.csv")
print(orders.shape)
orders.head()

actual_date = "order_delivered_customer_date"

# Convert the delivery date column from text to dates.
orders[actual_date] = pd.to_datetime(orders[actual_date], errors="coerce")

# Count missing dates among orders marked as delivered.
delivered = orders[orders["order_status"] == "delivered"]

print("Orders marked as delivered:", len(delivered))
print("Delivered orders with no usable delivery date:", delivered[actual_date].isna().sum())

purchase_date = "order_purchase_timestamp"
orders[purchase_date] = pd.to_datetime(orders[purchase_date], errors="coerce")

# Keep delivered orders with both dates available.
valid = orders.loc[orders["order_status"] == "delivered"].dropna(
    subset=[purchase_date, actual_date]
)

# Subtract purchase time from delivery time, then convert seconds to days.
elapsed = valid[actual_date] - valid[purchase_date]
days = elapsed.dt.total_seconds() / 86_400

print("Orders used:", len(valid))
print(f"Median delivery lead time: {days.median():.1f} days")

estimated_date = "order_estimated_delivery_date"
orders[estimated_date] = pd.to_datetime(orders[estimated_date], errors="coerce")

# Keep delivered orders with both dates available.
timing = orders.loc[orders["order_status"] == "delivered"].dropna(
    subset=[actual_date, estimated_date]
)

# Compare calendar dates so a delivery at any time that day counts as on time.
on_time = timing[actual_date].dt.normalize() <= timing[estimated_date].dt.normalize()

print("Orders used for on-time rate:", len(timing))
print("On-time deliveries:", on_time.sum())
print(f"On-time delivery rate: {on_time.mean():.2%}")

customers_path = Path(__file__).with_name("olist_customers_dataset.csv")
customers = pd.read_csv(customers_path)

print("\nCustomer data preview:")
print(customers[["customer_id", "customer_state"]].head())

print("Customer rows:", len(customers))
print("Unique customer IDs:", customers["customer_id"].nunique())


query = """
SELECT
    o.order_id,
    o.order_status,
    c.customer_id AS matched_customer_id,
    c.customer_state
FROM orders AS o
LEFT JOIN customers AS c
    ON o.customer_id = c.customer_id;
"""

# Create a temporary database and copy in the columns the query needs.
connection = sqlite3.connect(":memory:")

orders[["order_id", "customer_id", "order_status"]].to_sql(
    "orders", connection, index=False
)
customers[["customer_id", "customer_state"]].to_sql(
    "customers", connection, index=False
)

joined = pd.read_sql_query(query, connection)
connection.close()

print("\nOrders with customer state:")
print(joined[["order_id", "order_status", "customer_state"]].head())
print("Rows after the join:", len(joined))
print("Orders without a matching customer:", joined["matched_customer_id"].isna().sum())

# Reuse the orders with valid actual and estimated delivery dates.
delivery_results = timing[["order_id"]].copy()
delivery_results["is_late"] = ~on_time

# Attach customer state using the result of your SQL join.
delivery_results = delivery_results.merge(
    joined[["order_id", "customer_state"]],
    on="order_id",
    how="left",
    validate="one_to_one",
)

state_summary = delivery_results.groupby("customer_state").agg(
    deliveries=("order_id", "size"),
    late_deliveries=("is_late", "sum"),
)

state_summary["late_rate_pct"] = (
    100 * state_summary["late_deliveries"] / state_summary["deliveries"]
).round(2)

print("\nTop 5 states by number of late deliveries:")
print(state_summary.sort_values("late_deliveries", ascending=False).head(5))

output_path = Path(__file__).with_name("delivery_by_state.csv")

state_summary.sort_values("late_deliveries", ascending=False).to_csv(output_path)

print("\nSaved state summary to:", output_path)
