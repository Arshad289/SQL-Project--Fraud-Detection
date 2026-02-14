"""
SQL Fraud Detection -- Python Companion Script
==============================================
Author: Arshad Ali Mohammed
GitHub: https://github.com/Arshad289

Loads the credit card transactions dataset into a SQLite database,
executes the core fraud detection queries, and generates summary
visualizations. This allows the full analysis to run locally
without a PostgreSQL server.

Dataset: Simulated Credit Card Transaction Data (Kaggle)
https://www.kaggle.com/datasets/kartik2112/fraud-detection
"""

import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid")


# ──────────────────────────────────────────────────────────
# 1. LOAD DATA INTO SQLITE
# ──────────────────────────────────────────────────────────

def load_data(filepath: str = "data/fraudTrain.csv", db_path: str = ":memory:") -> sqlite3.Connection:
    """
    Load CSV into SQLite and return connection.

    Uses in-memory DB by default for speed and no leftover files.
    Pass a file path to db_path for persistence.
    """
    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath, parse_dates=["trans_date_trans_time"])
    print(f"Raw shape: {df.shape}")

    # Standardize column names
    df.columns = df.columns.str.strip().str.lower()

    # Derive useful columns before loading into SQLite
    df["txn_hour"] = df["trans_date_trans_time"].dt.hour
    df["txn_day_of_week"] = df["trans_date_trans_time"].dt.dayofweek  # 0=Mon, 6=Sun
    df["txn_month"] = df["trans_date_trans_time"].dt.to_period("M").astype(str)

    # Age at time of transaction
    df["dob"] = pd.to_datetime(df["dob"])
    df["age"] = ((df["trans_date_trans_time"] - df["dob"]).dt.days / 365.25).astype(int)
    df["age_group"] = pd.cut(
        df["age"], bins=[0, 25, 35, 45, 55, 65, 120],
        labels=["18-24", "25-34", "35-44", "45-54", "55-64", "65+"],
    )

    # Amount bucket
    df["amount_bucket"] = pd.cut(
        df["amt"], bins=[0, 100, 500, 1000, float("inf")],
        labels=["0-100", "100-500", "500-1000", "1000+"],
    )

    # City size
    df["city_size"] = pd.cut(
        df["city_pop"], bins=[0, 10_000, 100_000, 500_000, float("inf")],
        labels=["Rural (<10K)", "Small (10K-100K)", "Mid (100K-500K)", "Large (500K+)"],
    )

    conn = sqlite3.connect(db_path)
    df.to_sql("transactions", conn, if_exists="replace", index=False)
    print(f"[+] Loaded {len(df):,} rows into SQLite")
    return conn


# ──────────────────────────────────────────────────────────
# 2. CORE FRAUD QUERIES
# ──────────────────────────────────────────────────────────

def run_query(conn: sqlite3.Connection, sql: str) -> pd.DataFrame:
    """Execute a SQL query and return a DataFrame."""
    return pd.read_sql(sql, conn)


def fraud_overview(conn: sqlite3.Connection) -> None:
    """Print overall fraud statistics."""
    result = run_query(conn, """
        SELECT
            COUNT(*) AS total_txns,
            SUM(is_fraud) AS fraud_count,
            ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2) AS fraud_rate_pct,
            ROUND(AVG(amt), 2) AS avg_amount,
            ROUND(SUM(CASE WHEN is_fraud = 1 THEN amt ELSE 0 END), 2) AS total_fraud_amount
        FROM transactions
    """).iloc[0]
    print("\n" + "=" * 50)
    print("         FRAUD DETECTION OVERVIEW")
    print("=" * 50)
    print(f"  Total Transactions:   {int(result['total_txns']):>12,}")
    print(f"  Fraudulent Txns:      {int(result['fraud_count']):>12,}")
    print(f"  Fraud Rate:           {result['fraud_rate_pct']:>11}%")
    print(f"  Avg Transaction:      ${result['avg_amount']:>11}")
    print(f"  Total Fraud Amount:   ${result['total_fraud_amount']:>11,}")
    print("=" * 50)


def fraud_by_category(conn: sqlite3.Connection) -> pd.DataFrame:
    """Fraud rate by merchant category."""
    return run_query(conn, """
        SELECT
            category,
            COUNT(*) AS total_txns,
            SUM(is_fraud) AS fraud_txns,
            ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2) AS fraud_rate_pct,
            ROUND(AVG(CASE WHEN is_fraud = 1 THEN amt END), 2) AS avg_fraud_amt
        FROM transactions
        GROUP BY category
        ORDER BY fraud_rate_pct DESC
    """)


def fraud_by_hour(conn: sqlite3.Connection) -> pd.DataFrame:
    """Fraud rate by hour of day."""
    return run_query(conn, """
        SELECT
            txn_hour,
            COUNT(*) AS total_txns,
            SUM(is_fraud) AS fraud_txns,
            ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2) AS fraud_rate_pct
        FROM transactions
        GROUP BY txn_hour
        ORDER BY txn_hour
    """)


def fraud_by_day_of_week(conn: sqlite3.Connection) -> pd.DataFrame:
    """Fraud rate by day of week."""
    return run_query(conn, """
        SELECT
            txn_day_of_week,
            COUNT(*) AS total_txns,
            SUM(is_fraud) AS fraud_txns,
            ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2) AS fraud_rate_pct
        FROM transactions
        GROUP BY txn_day_of_week
        ORDER BY txn_day_of_week
    """)


def fraud_by_amount_bucket(conn: sqlite3.Connection) -> pd.DataFrame:
    """Fraud rate by transaction amount bucket."""
    return run_query(conn, """
        SELECT
            amount_bucket,
            COUNT(*) AS total_txns,
            SUM(is_fraud) AS fraud_txns,
            ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2) AS fraud_rate_pct
        FROM transactions
        GROUP BY amount_bucket
        ORDER BY fraud_rate_pct DESC
    """)


def fraud_by_state(conn: sqlite3.Connection, n: int = 15) -> pd.DataFrame:
    """Top N states by fraud count."""
    return run_query(conn, f"""
        SELECT
            state,
            COUNT(*) AS total_txns,
            SUM(is_fraud) AS fraud_txns,
            ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2) AS fraud_rate_pct
        FROM transactions
        GROUP BY state
        ORDER BY fraud_txns DESC
        LIMIT {n}
    """)


def fraud_by_gender(conn: sqlite3.Connection) -> pd.DataFrame:
    """Fraud rate by gender."""
    return run_query(conn, """
        SELECT
            gender,
            COUNT(*) AS total_txns,
            SUM(is_fraud) AS fraud_txns,
            ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2) AS fraud_rate_pct
        FROM transactions
        GROUP BY gender
    """)


def fraud_by_age_group(conn: sqlite3.Connection) -> pd.DataFrame:
    """Fraud rate by age group."""
    return run_query(conn, """
        SELECT
            age_group,
            COUNT(*) AS total_txns,
            SUM(is_fraud) AS fraud_txns,
            ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2) AS fraud_rate_pct
        FROM transactions
        WHERE age_group IS NOT NULL
        GROUP BY age_group
        ORDER BY fraud_rate_pct DESC
    """)


def fraud_by_city_size(conn: sqlite3.Connection) -> pd.DataFrame:
    """Fraud rate by city population size."""
    return run_query(conn, """
        SELECT
            city_size,
            COUNT(*) AS total_txns,
            SUM(is_fraud) AS fraud_txns,
            ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2) AS fraud_rate_pct
        FROM transactions
        WHERE city_size IS NOT NULL
        GROUP BY city_size
        ORDER BY fraud_rate_pct DESC
    """)


def repeat_fraud_cards(conn: sqlite3.Connection) -> pd.DataFrame:
    """Cards with 3+ fraud incidents."""
    return run_query(conn, """
        SELECT
            cc_num,
            COUNT(*) AS fraud_count,
            ROUND(SUM(amt), 2) AS total_fraud_amount,
            MIN(trans_date_trans_time) AS first_fraud,
            MAX(trans_date_trans_time) AS last_fraud
        FROM transactions
        WHERE is_fraud = 1
        GROUP BY cc_num
        HAVING COUNT(*) >= 3
        ORDER BY fraud_count DESC
        LIMIT 20
    """)


def high_risk_merchants(conn: sqlite3.Connection) -> pd.DataFrame:
    """Merchants with abnormally high fraud rates."""
    return run_query(conn, """
        SELECT
            merchant,
            category,
            COUNT(*) AS total_txns,
            SUM(is_fraud) AS fraud_txns,
            ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2) AS fraud_rate_pct,
            ROUND(SUM(CASE WHEN is_fraud = 1 THEN amt ELSE 0 END), 2) AS total_fraud_amount
        FROM transactions
        GROUP BY merchant, category
        HAVING COUNT(*) >= 20 AND SUM(is_fraud) >= 3
        ORDER BY fraud_rate_pct DESC
        LIMIT 20
    """)


def fraud_trend_monthly(conn: sqlite3.Connection) -> pd.DataFrame:
    """Monthly fraud rate trend."""
    return run_query(conn, """
        SELECT
            txn_month,
            COUNT(*) AS total_txns,
            SUM(is_fraud) AS fraud_txns,
            ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2) AS fraud_rate_pct
        FROM transactions
        GROUP BY txn_month
        ORDER BY txn_month
    """)


# ──────────────────────────────────────────────────────────
# 3. VISUALIZATIONS
# ──────────────────────────────────────────────────────────

def plot_fraud_by_category(df_cat: pd.DataFrame) -> None:
    """Bar chart of fraud rate by category."""
    fig, ax = plt.subplots(figsize=(10, 7))
    df_cat.sort_values("fraud_rate_pct").plot(
        x="category", y="fraud_rate_pct", kind="barh", ax=ax, color="crimson", legend=False
    )
    ax.set_title("Fraud Rate by Merchant Category", fontsize=14)
    ax.set_xlabel("Fraud Rate (%)")
    ax.set_ylabel("")
    plt.tight_layout()
    plt.savefig("outputs/fraud_rate_by_category.png", dpi=150)
    plt.close()
    print("[+] Saved fraud_rate_by_category.png")


def plot_fraud_by_hour(df_hour: pd.DataFrame) -> None:
    """Dual-axis: transaction volume bars + fraud rate line by hour."""
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(df_hour["txn_hour"], df_hour["total_txns"], alpha=0.3, color="steelblue", label="Total Txns")
    ax2 = ax.twinx()
    ax2.plot(df_hour["txn_hour"], df_hour["fraud_rate_pct"], color="red", marker="o", linewidth=2, label="Fraud Rate %")
    ax.set_title("Transaction Volume & Fraud Rate by Hour of Day", fontsize=14)
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Transaction Count")
    ax2.set_ylabel("Fraud Rate (%)")
    ax.legend(loc="upper left")
    ax2.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig("outputs/fraud_rate_by_hour.png", dpi=150)
    plt.close()
    print("[+] Saved fraud_rate_by_hour.png")


def plot_fraud_by_day(df_dow: pd.DataFrame) -> None:
    """Fraud rate by day of week."""
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(df_dow["txn_day_of_week"], df_dow["fraud_rate_pct"], color="teal")
    ax.set_xticks(range(7))
    ax.set_xticklabels(day_names)
    ax.set_title("Fraud Rate by Day of Week", fontsize=14)
    ax.set_ylabel("Fraud Rate (%)")
    ax.set_xlabel("Day of Week")
    plt.tight_layout()
    plt.savefig("outputs/fraud_rate_by_day.png", dpi=150)
    plt.close()
    print("[+] Saved fraud_rate_by_day.png")


def plot_fraud_by_amount(df_amt: pd.DataFrame) -> None:
    """Bar chart of fraud rate by amount bucket."""
    fig, ax = plt.subplots(figsize=(8, 5))
    df_amt.plot(x="amount_bucket", y="fraud_rate_pct", kind="bar", ax=ax, color="darkorange", legend=False)
    ax.set_title("Fraud Rate by Transaction Amount", fontsize=14)
    ax.set_ylabel("Fraud Rate (%)")
    ax.set_xlabel("Amount Bucket ($)")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig("outputs/fraud_rate_by_amount.png", dpi=150)
    plt.close()
    print("[+] Saved fraud_rate_by_amount.png")


def plot_amount_distribution(conn: sqlite3.Connection) -> None:
    """Histogram comparing legitimate vs fraudulent transaction amounts."""
    legit = run_query(conn, "SELECT amt FROM transactions WHERE is_fraud = 0")
    fraud = run_query(conn, "SELECT amt FROM transactions WHERE is_fraud = 1")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(legit["amt"], bins=50, alpha=0.5, label="Legitimate", color="steelblue", range=(0, 1500))
    ax.hist(fraud["amt"], bins=50, alpha=0.7, label="Fraudulent", color="crimson", range=(0, 1500))
    ax.set_title("Transaction Amount Distribution: Legitimate vs Fraudulent", fontsize=14)
    ax.set_xlabel("Amount ($)")
    ax.set_ylabel("Count")
    ax.legend()
    plt.tight_layout()
    plt.savefig("outputs/amount_distribution.png", dpi=150)
    plt.close()
    print("[+] Saved amount_distribution.png")


def plot_fraud_by_demographics(df_age: pd.DataFrame, df_gender: pd.DataFrame) -> None:
    """Side-by-side: fraud rate by age group and gender."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Age group
    df_age_sorted = df_age.sort_values("fraud_rate_pct", ascending=True)
    ax1.barh(df_age_sorted["age_group"].astype(str), df_age_sorted["fraud_rate_pct"], color="mediumpurple")
    ax1.set_title("Fraud Rate by Age Group", fontsize=13)
    ax1.set_xlabel("Fraud Rate (%)")

    # Gender
    ax2.bar(df_gender["gender"], df_gender["fraud_rate_pct"], color=["steelblue", "salmon"])
    ax2.set_title("Fraud Rate by Gender", fontsize=13)
    ax2.set_ylabel("Fraud Rate (%)")

    plt.tight_layout()
    plt.savefig("outputs/fraud_demographics.png", dpi=150)
    plt.close()
    print("[+] Saved fraud_demographics.png")


def plot_fraud_by_state(df_state: pd.DataFrame) -> None:
    """Top states by fraud count."""
    fig, ax = plt.subplots(figsize=(10, 6))
    df_state.sort_values("fraud_txns").plot(
        x="state", y="fraud_txns", kind="barh", ax=ax, color="darkred", legend=False
    )
    ax.set_title("Top 15 States by Fraud Count", fontsize=14)
    ax.set_xlabel("Fraud Transactions")
    ax.set_ylabel("")
    plt.tight_layout()
    plt.savefig("outputs/fraud_by_state.png", dpi=150)
    plt.close()
    print("[+] Saved fraud_by_state.png")


def plot_fraud_trend(df_trend: pd.DataFrame) -> None:
    """Monthly fraud rate trend line."""
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(range(len(df_trend)), df_trend["fraud_rate_pct"], marker="o", color="crimson", linewidth=2)
    ax.set_xticks(range(len(df_trend)))
    ax.set_xticklabels(df_trend["txn_month"], rotation=45, ha="right")
    ax.set_title("Monthly Fraud Rate Trend", fontsize=14)
    ax.set_ylabel("Fraud Rate (%)")
    ax.set_xlabel("Month")
    plt.tight_layout()
    plt.savefig("outputs/fraud_monthly_trend.png", dpi=150)
    plt.close()
    print("[+] Saved fraud_monthly_trend.png")


# ──────────────────────────────────────────────────────────
# 4. MAIN
# ──────────────────────────────────────────────────────────

def main():
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    conn = load_data()

    # Overview
    fraud_overview(conn)

    # Category analysis
    print("\n--- Fraud by Category ---")
    df_cat = fraud_by_category(conn)
    print(df_cat.to_string(index=False))

    # Temporal analysis
    print("\n--- Fraud by Hour ---")
    df_hour = fraud_by_hour(conn)
    print(df_hour.to_string(index=False))

    print("\n--- Fraud by Day of Week ---")
    df_dow = fraud_by_day_of_week(conn)
    print(df_dow.to_string(index=False))

    # Amount analysis
    print("\n--- Fraud by Amount Bucket ---")
    df_amt = fraud_by_amount_bucket(conn)
    print(df_amt.to_string(index=False))

    # Geographic analysis
    print("\n--- Fraud by State (Top 15) ---")
    df_state = fraud_by_state(conn)
    print(df_state.to_string(index=False))

    # Demographic analysis
    print("\n--- Fraud by Gender ---")
    df_gender = fraud_by_gender(conn)
    print(df_gender.to_string(index=False))

    print("\n--- Fraud by Age Group ---")
    df_age = fraud_by_age_group(conn)
    print(df_age.to_string(index=False))

    print("\n--- Fraud by City Size ---")
    df_city = fraud_by_city_size(conn)
    print(df_city.to_string(index=False))

    # Pattern detection
    print("\n--- Repeat Fraud Cards (Top 20) ---")
    df_repeat = repeat_fraud_cards(conn)
    print(df_repeat.to_string(index=False))

    print("\n--- High-Risk Merchants (Top 20) ---")
    df_merchants = high_risk_merchants(conn)
    print(df_merchants.to_string(index=False))

    # Trend
    print("\n--- Monthly Fraud Trend ---")
    df_trend = fraud_trend_monthly(conn)
    print(df_trend.to_string(index=False))

    # Visualizations
    print("\n--- Generating Visualizations ---")
    plot_fraud_by_category(df_cat)
    plot_fraud_by_hour(df_hour)
    plot_fraud_by_day(df_dow)
    plot_fraud_by_amount(df_amt)
    plot_amount_distribution(conn)
    plot_fraud_by_demographics(df_age, df_gender)
    plot_fraud_by_state(df_state)
    plot_fraud_trend(df_trend)

    # Export results
    for name, data in [
        ("fraud_by_category", df_cat),
        ("fraud_by_hour", df_hour),
        ("fraud_by_day_of_week", df_dow),
        ("fraud_by_amount", df_amt),
        ("fraud_by_state", df_state),
        ("fraud_by_gender", df_gender),
        ("fraud_by_age_group", df_age),
        ("fraud_by_city_size", df_city),
        ("repeat_fraud_cards", df_repeat),
        ("high_risk_merchants", df_merchants),
        ("fraud_monthly_trend", df_trend),
    ]:
        data.to_csv(f"outputs/{name}.csv", index=False)

    print(f"\n[+] Exported {11} CSV files to outputs/")

    conn.close()
    print("[+] Analysis complete!")


if __name__ == "__main__":
    main()
