-- ============================================================
-- SQL Project: Credit Card Fraud Detection
-- Author: Arshad Ali Mohammed
-- GitHub: https://github.com/Arshad289
--
-- Analyzes 1,300,000+ credit card transactions to identify
-- potentially fraudulent activities using SQL queries.
--
-- Dataset: Credit Card Transactions (Kaggle)
-- https://www.kaggle.com/datasets/kartik2112/fraud-detection
-- ============================================================


-- ============================================================
-- 1. DATABASE SETUP & TABLE CREATION
-- ============================================================

CREATE TABLE IF NOT EXISTS transactions (
    trans_id            VARCHAR(50) PRIMARY KEY,
    trans_date_trans_time TIMESTAMP,
    cc_num              BIGINT,
    merchant            VARCHAR(200),
    category            VARCHAR(100),
    amt                 DECIMAL(10, 2),
    first_name          VARCHAR(100),
    last_name           VARCHAR(100),
    gender              CHAR(1),
    street              VARCHAR(200),
    city                VARCHAR(100),
    state               CHAR(2),
    zip                 INT,
    lat                 DECIMAL(10, 6),
    long                DECIMAL(10, 6),
    city_pop            INT,
    job                 VARCHAR(200),
    dob                 DATE,
    trans_num           VARCHAR(100),
    unix_time           BIGINT,
    merch_lat           DECIMAL(10, 6),
    merch_long          DECIMAL(10, 6),
    is_fraud            INT  -- 0 = legitimate, 1 = fraudulent
);

-- ============================================================
-- RECOMMENDED INDEXES FOR PRODUCTION (OPTIONAL)
-- ============================================================
-- Uncomment these indexes for faster query performance on large datasets:
-- 
-- CREATE INDEX idx_trans_date ON transactions(trans_date_trans_time);
-- CREATE INDEX idx_cc_num ON transactions(cc_num);
-- CREATE INDEX idx_is_fraud ON transactions(is_fraud);
-- CREATE INDEX idx_category ON transactions(category);
-- CREATE INDEX idx_merchant ON transactions(merchant);
-- CREATE INDEX idx_state ON transactions(state);
-- CREATE INDEX idx_amount ON transactions(amt);
--
-- For geographic queries:
-- CREATE INDEX idx_lat_long ON transactions(lat, long);
-- CREATE INDEX idx_merch_lat_long ON transactions(merch_lat, merch_long);
-- ============================================================


-- ============================================================
-- 2. DATA OVERVIEW
-- ============================================================

-- 2a. Total record count and fraud rate
SELECT
    COUNT(*)                                AS total_transactions,
    SUM(is_fraud)                           AS fraud_count,
    ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2) AS fraud_rate_pct
FROM transactions;


-- 2b. Date range of the dataset
SELECT
    MIN(trans_date_trans_time) AS earliest_transaction,
    MAX(trans_date_trans_time) AS latest_transaction
FROM transactions;


-- 2c. Unique counts
SELECT
    COUNT(DISTINCT cc_num)   AS unique_cards,
    COUNT(DISTINCT merchant) AS unique_merchants,
    COUNT(DISTINCT category) AS unique_categories,
    COUNT(DISTINCT state)    AS unique_states
FROM transactions;


-- ============================================================
-- 3. FRAUD DISTRIBUTION ANALYSIS
-- ============================================================

-- 3a. Fraud count & rate by merchant category
SELECT
    category,
    COUNT(*)                                     AS total_txns,
    SUM(is_fraud)                                AS fraud_txns,
    ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2)  AS fraud_rate_pct,
    ROUND(AVG(CASE WHEN is_fraud = 1 THEN amt END), 2) AS avg_fraud_amount
FROM transactions
GROUP BY category
ORDER BY fraud_rate_pct DESC;


-- 3b. Fraud by state (top 10)
SELECT
    state,
    COUNT(*)                                    AS total_txns,
    SUM(is_fraud)                               AS fraud_txns,
    ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2) AS fraud_rate_pct
FROM transactions
GROUP BY state
ORDER BY fraud_txns DESC
LIMIT 10;


-- 3c. Fraud by hour of day
SELECT
    EXTRACT(HOUR FROM trans_date_trans_time) AS txn_hour,
    COUNT(*)                                AS total_txns,
    SUM(is_fraud)                           AS fraud_txns,
    ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2) AS fraud_rate_pct
FROM transactions
GROUP BY txn_hour
ORDER BY txn_hour;


-- 3d. Fraud by day of week (0=Sun, 6=Sat)
SELECT
    EXTRACT(DOW FROM trans_date_trans_time) AS day_of_week,
    COUNT(*)                               AS total_txns,
    SUM(is_fraud)                          AS fraud_txns,
    ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2) AS fraud_rate_pct
FROM transactions
GROUP BY day_of_week
ORDER BY day_of_week;


-- ============================================================
-- 4. TRANSACTION AMOUNT ANALYSIS
-- ============================================================

-- 4a. Compare legitimate vs fraudulent transaction amounts
SELECT
    CASE WHEN is_fraud = 1 THEN 'Fraudulent' ELSE 'Legitimate' END AS txn_type,
    COUNT(*)            AS txn_count,
    ROUND(AVG(amt), 2)  AS avg_amount,
    ROUND(MIN(amt), 2)  AS min_amount,
    ROUND(MAX(amt), 2)  AS max_amount,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amt), 2) AS median_amount
FROM transactions
GROUP BY is_fraud;


-- 4b. High-value transactions (> $500) fraud rate
SELECT
    CASE
        WHEN amt <= 100 THEN '0-100'
        WHEN amt <= 500 THEN '100-500'
        WHEN amt <= 1000 THEN '500-1000'
        ELSE '1000+'
    END AS amount_bucket,
    COUNT(*)                                    AS total_txns,
    SUM(is_fraud)                               AS fraud_txns,
    ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2) AS fraud_rate_pct
FROM transactions
GROUP BY amount_bucket
ORDER BY fraud_rate_pct DESC;


-- ============================================================
-- 5. FLAGGING SUSPICIOUS PATTERNS
-- ============================================================

-- 5a. Cards with multiple fraud incidents
SELECT
    cc_num,
    COUNT(*)                       AS fraud_count,
    ROUND(SUM(amt), 2)            AS total_fraud_amount,
    MIN(trans_date_trans_time)     AS first_fraud,
    MAX(trans_date_trans_time)     AS last_fraud
FROM transactions
WHERE is_fraud = 1
GROUP BY cc_num
HAVING COUNT(*) >= 3
ORDER BY fraud_count DESC
LIMIT 20;


-- 5b. Rapid successive transactions on the same card (within 10 minutes)
WITH txn_pairs AS (
    SELECT
        t1.cc_num,
        t1.trans_id AS txn1_id,
        t2.trans_id AS txn2_id,
        t1.amt      AS amt1,
        t2.amt      AS amt2,
        t1.trans_date_trans_time AS time1,
        t2.trans_date_trans_time AS time2,
        EXTRACT(EPOCH FROM (t2.trans_date_trans_time - t1.trans_date_trans_time)) / 60 AS minutes_apart
    FROM transactions t1
    JOIN transactions t2
        ON  t1.cc_num = t2.cc_num
        AND t2.trans_date_trans_time > t1.trans_date_trans_time
        AND t2.trans_date_trans_time <= t1.trans_date_trans_time + INTERVAL '10 minutes'
    WHERE t1.is_fraud = 1 OR t2.is_fraud = 1
)
SELECT *
FROM txn_pairs
ORDER BY minutes_apart ASC
LIMIT 20;


-- 5c. Geographically distant transactions within 1 hour (possible card cloning)
WITH geo_pairs AS (
    SELECT
        t1.cc_num,
        t1.trans_id AS txn1,
        t2.trans_id AS txn2,
        t1.city AS city1,
        t2.city AS city2,
        t1.state AS state1,
        t2.state AS state2,
        EXTRACT(EPOCH FROM (t2.trans_date_trans_time - t1.trans_date_trans_time)) / 60 AS minutes_apart,
        -- Haversine approximation (miles)
        3959 * ACOS(
            LEAST(1, COS(RADIANS(t1.lat)) * COS(RADIANS(t2.lat))
            * COS(RADIANS(t2.long) - RADIANS(t1.long))
            + SIN(RADIANS(t1.lat)) * SIN(RADIANS(t2.lat)))
        ) AS distance_miles
    FROM transactions t1
    JOIN transactions t2
        ON  t1.cc_num = t2.cc_num
        AND t2.trans_date_trans_time > t1.trans_date_trans_time
        AND t2.trans_date_trans_time <= t1.trans_date_trans_time + INTERVAL '1 hour'
        AND t1.trans_id != t2.trans_id
)
SELECT *
FROM geo_pairs
WHERE distance_miles > 100
ORDER BY distance_miles DESC
LIMIT 20;


-- 5d. Merchants with abnormally high fraud rates
SELECT
    merchant,
    category,
    COUNT(*)                                    AS total_txns,
    SUM(is_fraud)                               AS fraud_txns,
    ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2) AS fraud_rate_pct,
    ROUND(SUM(CASE WHEN is_fraud = 1 THEN amt ELSE 0 END), 2) AS total_fraud_amount
FROM transactions
GROUP BY merchant, category
HAVING COUNT(*) >= 20 AND SUM(is_fraud) >= 3
ORDER BY fraud_rate_pct DESC
LIMIT 20;


-- ============================================================
-- 6. DEMOGRAPHIC PATTERNS
-- ============================================================

-- 6a. Fraud rate by gender
SELECT
    gender,
    COUNT(*)                                    AS total_txns,
    SUM(is_fraud)                               AS fraud_txns,
    ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2) AS fraud_rate_pct
FROM transactions
GROUP BY gender;


-- 6b. Fraud rate by age group
SELECT
    CASE
        WHEN EXTRACT(YEAR FROM AGE(trans_date_trans_time, dob)) < 25 THEN '18-24'
        WHEN EXTRACT(YEAR FROM AGE(trans_date_trans_time, dob)) < 35 THEN '25-34'
        WHEN EXTRACT(YEAR FROM AGE(trans_date_trans_time, dob)) < 45 THEN '35-44'
        WHEN EXTRACT(YEAR FROM AGE(trans_date_trans_time, dob)) < 55 THEN '45-54'
        WHEN EXTRACT(YEAR FROM AGE(trans_date_trans_time, dob)) < 65 THEN '55-64'
        ELSE '65+'
    END AS age_group,
    COUNT(*)                                    AS total_txns,
    SUM(is_fraud)                               AS fraud_txns,
    ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2) AS fraud_rate_pct
FROM transactions
GROUP BY age_group
ORDER BY fraud_rate_pct DESC;


-- 6c. Fraud rate by city population size
SELECT
    CASE
        WHEN city_pop < 10000  THEN 'Rural (<10K)'
        WHEN city_pop < 100000 THEN 'Small City (10K-100K)'
        WHEN city_pop < 500000 THEN 'Mid City (100K-500K)'
        ELSE 'Large City (500K+)'
    END AS city_size,
    COUNT(*)                                    AS total_txns,
    SUM(is_fraud)                               AS fraud_txns,
    ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2) AS fraud_rate_pct
FROM transactions
GROUP BY city_size
ORDER BY fraud_rate_pct DESC;


-- ============================================================
-- 7. SUMMARY VIEW: FRAUD RISK SCORE CARD
-- ============================================================

CREATE OR REPLACE VIEW fraud_risk_scorecard AS
SELECT
    category,
    state,
    EXTRACT(HOUR FROM trans_date_trans_time) AS txn_hour,
    CASE
        WHEN amt > 500 THEN 'High Value'
        WHEN amt > 100 THEN 'Medium Value'
        ELSE 'Low Value'
    END AS value_tier,
    COUNT(*)                                    AS total_txns,
    SUM(is_fraud)                               AS fraud_txns,
    ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2) AS fraud_rate_pct,
    ROUND(AVG(amt), 2)                          AS avg_txn_amount
FROM transactions
GROUP BY category, state, txn_hour, value_tier
HAVING COUNT(*) >= 10;


-- Example: query the scorecard for high-risk combinations
SELECT *
FROM fraud_risk_scorecard
WHERE fraud_rate_pct > 5
ORDER BY fraud_rate_pct DESC
LIMIT 25;
