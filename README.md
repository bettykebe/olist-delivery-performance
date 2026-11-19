# Olist Delivery Performance by State

![Power BI report showing delivery performance by Brazilian state](dashboard.png)

## Business question

Which states should an operations team prioritize when investigating late deliveries?

## What I built

I used Python and pandas to clean delivery dates, SQLite to join orders
with customer states, and Power BI to build an interactive report with
delivery KPIs and a state filter.

## Key finding

Of 96,470 deliveries with usable dates, 93.23% arrived on time.
São Paulo had the most late deliveries (1,820). Rio de Janeiro had
1,495 late deliveries and a late rate of 12.11%, compared with 4.49%
in São Paulo. That makes Rio de Janeiro a priority for investigating
what drove the delays.

## Data source

[Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)