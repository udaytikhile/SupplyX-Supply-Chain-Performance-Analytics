-- ==============================================================================
-- SupplyX: 15 Documented Analytical SQL Queries
-- Database: data/supplyx.db (SQLite Star Schema)
-- Designed for operational diagnostics, SLA adherence, and executive visibility.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- QUERY 1: Delivery Performance & SLA Adherence by Geographic Market
-- Purpose: Evaluates regional fulfillment volume, late shipment percentage,
--          and the average delay between promised vs actual delivery days.
-- ------------------------------------------------------------------------------
-- @query_id: Q01_market_delivery_performance
SELECT
    g.market,
    COUNT(DISTINCT f.order_id) AS total_orders,
    COUNT(f.order_item_id) AS total_order_items,
    ROUND(SUM(f.order_item_total), 2) AS total_net_revenue,
    SUM(f.late_delivery_risk) AS late_shipment_count,
    ROUND(AVG(f.late_delivery_risk) * 100.0, 2) AS late_delivery_rate_pct,
    ROUND(AVG(f.days_shipping_real), 2) AS avg_real_shipping_days,
    ROUND(AVG(f.days_shipping_scheduled), 2) AS avg_scheduled_shipping_days,
    ROUND(AVG(f.shipping_delay_days), 2) AS avg_delay_gap_days
FROM fact_order_items f
JOIN dim_geography g ON f.geo_id = g.geo_id
GROUP BY g.market
ORDER BY total_net_revenue DESC;


-- ------------------------------------------------------------------------------
-- QUERY 2: Fulfillment Speed & Late Delivery Rate by Shipping Mode
-- Purpose: Pinpoints which transit class causes the highest delivery SLA breach.
-- Insight: Exposes the artificial rigidity in First Class (1 day scheduled) vs Standard (4 days).
-- ------------------------------------------------------------------------------
-- @query_id: Q02_shipping_mode_fulfillment
SELECT
    m.shipping_mode,
    COUNT(f.order_item_id) AS total_shipments,
    ROUND(COUNT(f.order_item_id) * 100.0 / (SELECT COUNT(*) FROM fact_order_items), 2) AS volume_share_pct,
    SUM(f.late_delivery_risk) AS late_count,
    ROUND(AVG(f.late_delivery_risk) * 100.0, 2) AS late_rate_pct,
    ROUND(AVG(f.days_shipping_real), 2) AS avg_actual_days,
    ROUND(AVG(f.days_shipping_scheduled), 2) AS avg_promised_days,
    ROUND(AVG(f.shipping_delay_days), 2) AS avg_days_over_promise
FROM fact_order_items f
JOIN dim_shipping_mode m ON f.shipping_mode_id = m.shipping_mode_id
GROUP BY m.shipping_mode
ORDER BY avg_days_over_promise DESC;


-- ------------------------------------------------------------------------------
-- QUERY 3: Late Delivery Hotspots by Product Category (Top 10 Categories)
-- Purpose: Identifies product categories with highest delivery friction and order volume.
-- ------------------------------------------------------------------------------
-- @query_id: Q03_category_late_hotspots
SELECT
    p.category_name,
    p.department_name,
    COUNT(f.order_item_id) AS item_volume,
    ROUND(SUM(f.order_item_total), 2) AS total_sales,
    SUM(f.late_delivery_risk) AS late_deliveries,
    ROUND(AVG(f.late_delivery_risk) * 100.0, 2) AS late_rate_pct,
    ROUND(AVG(f.days_shipping_real), 2) AS avg_shipping_days
FROM fact_order_items f
JOIN dim_product p ON f.product_card_id = p.product_card_id
GROUP BY p.category_name, p.department_name
HAVING COUNT(f.order_item_id) >= 1000
ORDER BY late_deliveries DESC
LIMIT 10;


-- ------------------------------------------------------------------------------
-- QUERY 4: Monthly Revenue, Order Volume & Late Rate Time Trends
-- Purpose: Analyzes long-term trend lines (2015-2018) and flags structural shifts.
-- ------------------------------------------------------------------------------
-- @query_id: Q04_monthly_performance_trend
SELECT
    d.year,
    d.month,
    d.year || '-' || printf('%02d', d.month) AS year_month,
    COUNT(DISTINCT f.order_id) AS monthly_orders,
    COUNT(f.order_item_id) AS monthly_items,
    ROUND(SUM(f.order_item_total), 2) AS monthly_revenue,
    ROUND(SUM(f.order_profit_per_order), 2) AS monthly_profit,
    ROUND(AVG(f.late_delivery_risk) * 100.0, 2) AS late_rate_pct,
    ROUND(AVG(f.days_shipping_real), 2) AS avg_transit_days
FROM fact_order_items f
JOIN dim_date d ON f.order_date_key = d.date_key
GROUP BY d.year, d.month, year_month
ORDER BY d.year, d.month;


-- ------------------------------------------------------------------------------
-- QUERY 5: On-Time vs. Late Order Profitability & Margin Comparison
-- Purpose: Tests whether late deliveries correlate with lower profit margins or discounts.
-- ------------------------------------------------------------------------------
-- @query_id: Q05_ontime_vs_late_profitability
SELECT
    CASE 
        WHEN f.late_delivery_risk = 1 THEN 'Late Delivery'
        WHEN f.delivery_status = 'Shipping canceled' THEN 'Shipping Canceled'
        ELSE 'On-Time / Early'
    END AS fulfillment_status,
    COUNT(f.order_item_id) AS item_count,
    ROUND(SUM(f.sales), 2) AS gross_sales,
    ROUND(SUM(f.order_item_discount), 2) AS total_discount,
    ROUND(SUM(f.order_item_total), 2) AS net_revenue,
    ROUND(SUM(f.order_profit_per_order), 2) AS net_profit,
    ROUND(SUM(f.order_profit_per_order) * 100.0 / SUM(f.order_item_total), 2) AS operating_margin_pct,
    ROUND(AVG(f.order_item_discount_rate) * 100.0, 2) AS avg_discount_rate_pct
FROM fact_order_items f
GROUP BY fulfillment_status
ORDER BY net_revenue DESC;


-- ------------------------------------------------------------------------------
-- QUERY 6: Customer Segment Delivery Performance
-- Purpose: Evaluates SLA adherence across Consumer, Corporate, and Home Office clients.
-- ------------------------------------------------------------------------------
-- @query_id: Q06_customer_segment_sla
SELECT
    c.customer_segment,
    COUNT(DISTINCT f.order_id) AS total_orders,
    COUNT(f.order_item_id) AS total_items,
    ROUND(SUM(f.order_item_total), 2) AS net_revenue,
    ROUND(AVG(f.late_delivery_risk) * 100.0, 2) AS late_rate_pct,
    ROUND(AVG(f.days_shipping_real), 2) AS avg_actual_days,
    ROUND(AVG(f.days_shipping_scheduled), 2) AS avg_promised_days
FROM fact_order_items f
JOIN dim_customer c ON f.customer_id = c.customer_id
GROUP BY c.customer_segment
ORDER BY net_revenue DESC;


-- ------------------------------------------------------------------------------
-- QUERY 7: Shipping Duration Discrepancy Breakdown (Real vs Scheduled Days)
-- Purpose: Builds an operational histogram of fulfillment delay variance.
-- ------------------------------------------------------------------------------
-- @query_id: Q07_delay_variance_distribution
SELECT
    f.shipping_delay_days,
    COUNT(f.order_item_id) AS shipment_count,
    ROUND(COUNT(f.order_item_id) * 100.0 / (SELECT COUNT(*) FROM fact_order_items), 2) AS share_of_shipments_pct,
    CASE
        WHEN f.shipping_delay_days < 0 THEN 'Early Delivery'
        WHEN f.shipping_delay_days = 0 THEN 'Exact On-Time'
        WHEN f.shipping_delay_days = 1 THEN '1 Day Late'
        WHEN f.shipping_delay_days = 2 THEN '2 Days Late'
        ELSE '3+ Days Late'
    END AS delay_category
FROM fact_order_items f
GROUP BY f.shipping_delay_days, delay_category
ORDER BY f.shipping_delay_days;


-- ------------------------------------------------------------------------------
-- QUERY 8: Cancellation Rate & Lost Sales by Destination Region (Top 10)
-- Purpose: Highlights geographic regions suffering high cancellation risk.
-- ------------------------------------------------------------------------------
-- @query_id: Q08_regional_cancellation_rates
SELECT
    g.order_region,
    g.market,
    COUNT(f.order_item_id) AS total_items,
    SUM(f.is_canceled) AS canceled_items,
    ROUND(AVG(f.is_canceled) * 100.0, 2) AS cancellation_rate_pct,
    ROUND(SUM(CASE WHEN f.is_canceled = 1 THEN f.order_item_total ELSE 0 END), 2) AS lost_sales_value
FROM fact_order_items f
JOIN dim_geography g ON f.geo_id = g.geo_id
GROUP BY g.order_region, g.market
HAVING COUNT(f.order_item_id) >= 2000
ORDER BY cancellation_rate_pct DESC
LIMIT 10;


-- ------------------------------------------------------------------------------
-- QUERY 9: Product Department Revenue vs Fulfillment Risk Matrix
-- Purpose: Classifies business units by commercial scale and delivery vulnerability.
-- ------------------------------------------------------------------------------
-- @query_id: Q09_department_risk_matrix
SELECT
    p.department_name,
    COUNT(DISTINCT f.order_id) AS orders_handled,
    ROUND(SUM(f.order_item_total), 2) AS total_revenue,
    ROUND(SUM(f.order_profit_per_order), 2) AS total_profit,
    ROUND(AVG(f.late_delivery_risk) * 100.0, 2) AS late_delivery_rate_pct,
    ROUND(AVG(f.days_shipping_real), 2) AS avg_fulfillment_days,
    ROUND(AVG(f.is_negative_profit) * 100.0, 2) AS loss_order_pct
FROM fact_order_items f
JOIN dim_product p ON f.product_card_id = p.product_card_id
GROUP BY p.department_name
ORDER BY total_revenue DESC;


-- ------------------------------------------------------------------------------
-- QUERY 10: Origin Store State to Destination Country Delay Bottlenecks
-- Purpose: Pinpoints multi-national transit corridors with severe delays.
-- ------------------------------------------------------------------------------
-- @query_id: Q10_corridor_fulfillment_delays
SELECT
    c.customer_state AS origin_store_state,
    g.order_country AS destination_country,
    g.market,
    COUNT(f.order_item_id) AS shipment_volume,
    ROUND(AVG(f.late_delivery_risk) * 100.0, 2) AS late_rate_pct,
    ROUND(AVG(f.days_shipping_real), 2) AS avg_shipping_days,
    ROUND(AVG(f.shipping_delay_days), 2) AS avg_delay_days
FROM fact_order_items f
JOIN dim_customer c ON f.customer_id = c.customer_id
JOIN dim_geography g ON f.geo_id = g.geo_id
GROUP BY c.customer_state, g.order_country, g.market
HAVING COUNT(f.order_item_id) >= 1500
ORDER BY avg_delay_days DESC
LIMIT 10;


-- ------------------------------------------------------------------------------
-- QUERY 11: Discount Depth vs Profit Erosion and Order Volume
-- Purpose: Evaluates margin degradation across markdown tiers.
-- ------------------------------------------------------------------------------
-- @query_id: Q11_discount_depth_impact
SELECT
    CASE
        WHEN f.order_item_discount_rate = 0 THEN '0% Full Price'
        WHEN f.order_item_discount_rate <= 0.05 THEN '1% - 5% Discount'
        WHEN f.order_item_discount_rate <= 0.10 THEN '6% - 10% Discount'
        WHEN f.order_item_discount_rate <= 0.15 THEN '11% - 15% Discount'
        WHEN f.order_item_discount_rate <= 0.20 THEN '16% - 20% Discount'
        ELSE '> 20% Deep Discount'
    END AS discount_tier,
    COUNT(f.order_item_id) AS item_count,
    ROUND(SUM(f.sales), 2) AS gross_sales,
    ROUND(SUM(f.order_item_discount), 2) AS discount_absorbed,
    ROUND(SUM(f.order_item_total), 2) AS net_revenue,
    ROUND(SUM(f.order_profit_per_order), 2) AS net_profit,
    ROUND(SUM(f.order_profit_per_order) * 100.0 / SUM(f.order_item_total), 2) AS profit_margin_pct,
    SUM(f.is_negative_profit) AS loss_making_items,
    ROUND(AVG(f.is_negative_profit) * 100.0, 2) AS loss_rate_pct
FROM fact_order_items f
GROUP BY discount_tier
ORDER BY MIN(f.order_item_discount_rate);


-- ------------------------------------------------------------------------------
-- QUERY 12: Shipping Mode SLA Adherence by Day Threshold
-- Purpose: Analyzes how often shipments fail their promised transit threshold.
-- ------------------------------------------------------------------------------
-- @query_id: Q12_mode_sla_breach_analysis
SELECT
    m.shipping_mode,
    f.days_shipping_scheduled AS promised_days,
    COUNT(f.order_item_id) AS total_shipments,
    SUM(CASE WHEN f.days_shipping_real <= f.days_shipping_scheduled THEN 1 ELSE 0 END) AS on_or_ahead_schedule,
    SUM(CASE WHEN f.days_shipping_real > f.days_shipping_scheduled THEN 1 ELSE 0 END) AS breached_schedule,
    ROUND(AVG(CASE WHEN f.days_shipping_real > f.days_shipping_scheduled THEN 1.0 ELSE 0.0 END) * 100.0, 2) AS breach_rate_pct
FROM fact_order_items f
JOIN dim_shipping_mode m ON f.shipping_mode_id = m.shipping_mode_id
GROUP BY m.shipping_mode, f.days_shipping_scheduled
ORDER BY breach_rate_pct DESC;


-- ------------------------------------------------------------------------------
-- QUERY 13: Customer Repeat Purchase Frequency & Delivery Reliability
-- Purpose: Examines whether loyal repeat customers experience consistent SLA delivery.
-- ------------------------------------------------------------------------------
-- @query_id: Q13_repeat_customer_sla
WITH customer_orders AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS order_frequency
    FROM fact_order_items
    GROUP BY customer_id
),
customer_tiers AS (
    SELECT
        customer_id,
        CASE
            WHEN order_frequency = 1 THEN '1 Order (One-Time)'
            WHEN order_frequency BETWEEN 2 AND 4 THEN '2 - 4 Orders (Occasional)'
            WHEN order_frequency BETWEEN 5 AND 9 THEN '5 - 9 Orders (Frequent)'
            ELSE '10+ Orders (VIP)'
        END AS loyalty_tier
    FROM customer_orders
)
SELECT
    t.loyalty_tier,
    COUNT(DISTINCT f.customer_id) AS unique_customers,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(SUM(f.order_item_total), 2) AS total_spend,
    ROUND(AVG(f.late_delivery_risk) * 100.0, 2) AS late_delivery_rate_pct,
    ROUND(AVG(f.days_shipping_real), 2) AS avg_shipping_days
FROM fact_order_items f
JOIN customer_tiers t ON f.customer_id = t.customer_id
GROUP BY t.loyalty_tier
ORDER BY total_spend DESC;


-- ------------------------------------------------------------------------------
-- QUERY 14: Day-of-Week Order Placement Velocity vs Shipping Delay
-- Purpose: Evaluates whether orders placed on specific weekdays suffer higher delays.
-- ------------------------------------------------------------------------------
-- @query_id: Q14_day_of_week_velocity
SELECT
    d.day_of_week,
    COUNT(DISTINCT f.order_id) AS orders_placed,
    COUNT(f.order_item_id) AS items_ordered,
    ROUND(AVG(f.late_delivery_risk) * 100.0, 2) AS late_rate_pct,
    ROUND(AVG(f.days_shipping_real), 2) AS avg_shipping_days,
    ROUND(AVG(f.shipping_delay_days), 2) AS avg_delay_days
FROM fact_order_items f
JOIN dim_date d ON f.order_date_key = d.date_key
GROUP BY d.day_of_week
ORDER BY orders_placed DESC;


-- ------------------------------------------------------------------------------
-- QUERY 15: Financial Summary & Explicit Shipping Cost Limitation Disclosure
-- Purpose: Consolidated commercial summary presenting verified revenues and profits,
--          with standard enterprise disclosure that freight costs are not recorded.
-- ------------------------------------------------------------------------------
-- @query_id: Q15_financial_summary_with_disclosure
SELECT
    COUNT(DISTINCT f.order_id) AS total_orders_billed,
    COUNT(f.order_item_id) AS total_line_items,
    ROUND(SUM(f.sales), 2) AS gross_catalog_sales,
    ROUND(SUM(f.order_item_discount), 2) AS total_promotional_markdown,
    ROUND(SUM(f.order_item_total), 2) AS net_revenue_collected,
    ROUND(SUM(f.order_profit_per_order), 2) AS net_operating_profit,
    ROUND(SUM(f.order_profit_per_order) * 100.0 / SUM(f.order_item_total), 2) AS operating_profit_margin_pct,
    'CARRIER_FREIGHT_COST_ABSENT_IN_DATACO_CORE' AS freight_cost_field_status,
    'Carrier shipping cost is not captured in source data. Model-based freight estimate available in Milestone 7.' AS data_limitation_disclosure
FROM fact_order_items f;
