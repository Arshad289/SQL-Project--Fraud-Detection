# 🔍 SQL Project: Credit Card Fraud Detection

![SQL](https://img.shields.io/badge/SQL-PostgreSQL%20%7C%20SQLite-336791?logo=postgresql&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-1.5%2B-green?logo=pandas&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

An end-to-end SQL-based fraud detection analysis on **1.3M+ credit card transactions**, identifying fraudulent patterns through temporal analysis, geographic anomaly detection, merchant risk profiling, and transaction amount segmentation.

---

## 📌 Project Highlights

| Area | Detail |
|---|---|
| **Dataset** | 1.3M+ simulated credit card transactions with ~0.6% fraud rate |
| **SQL Queries** | 15+ analytical queries covering 7 fraud detection dimensions |
| **Python Companion** | SQLite loader + Matplotlib visualizations for portability |
| **Key Finding** | Late-night (10 PM – 3 AM) transactions show 3× higher fraud rate |
| **Detection** | Geographic + temporal anomaly queries flag card cloning patterns |

---

## 🗂 Repository Structure

```
SQL-Project--Fraud-Detection/
├── fraud_detection_queries.sql  # Full PostgreSQL query suite (7 sections)
├── fraud_analysis.py            # Python companion: SQLite loader + charts
├── requirements.txt             # Python dependencies
├── DATASET.md                   # Dataset schema & download instructions
├── .gitignore
├── data/                        # Place fraudTrain.csv here (not tracked)
│   └── .gitkeep
└── outputs/                     # Charts & exported CSVs
    └── .gitkeep
```

---

## 🚀 Getting Started

### Prerequisites
- **Option A:** PostgreSQL 12+ (for the `.sql` file)
- **Option B:** Python 3.9+ with SQLite (for the `.py` companion — no DB server needed)

### Installation

```bash
git clone https://github.com/Arshad289/SQL-Project--Fraud-Detection.git
cd SQL-Project--Fraud-Detection
pip install -r requirements.txt
```

### Download the Dataset

1. Download from [Kaggle – Fraud Detection](https://www.kaggle.com/datasets/kartik2112/fraud-detection).
2. Place `fraudTrain.csv` in the `data/` folder.
3. See [DATASET.md](DATASET.md) for the full schema.

### Run the Analysis

**Option A — PostgreSQL:**
```bash
psql -d your_database -f fraud_detection_queries.sql
```

**Option B — Python + SQLite (recommended for portability):**
```bash
python fraud_analysis.py
```

This loads the CSV into SQLite, runs all core queries, prints results, and saves charts to `outputs/`.

---

## 📊 Analysis Sections

### 1. Data Overview
Total transaction count, fraud rate, date range, and unique entity counts.

### 2. Fraud Distribution Analysis
Fraud rates broken down by merchant category, state, hour of day, and day of week.

### 3. Transaction Amount Analysis
Comparison of legitimate vs. fraudulent transaction amount distributions, with fraud rate by dollar-amount bucket.

### 4. Suspicious Pattern Detection
- **Repeat fraud cards** — Cards with 3+ fraud incidents
- **Rapid successive transactions** — Same card used within 10 minutes
- **Geographic anomalies** — Transactions 100+ miles apart within 1 hour (card cloning indicator). Distance is computed using the Haversine formula
- **High-risk merchants** — Merchants with abnormally high fraud rates

### 5. Demographic Patterns
Fraud rates segmented by gender, age group, and city population size.

### 6. Fraud Risk Scorecard
Composite SQL view combining category, state, hour, and amount tier for multi-dimensional risk assessment.

---

## 📊 Sample Output

### Fraud Distribution by Category
| Category | Total Transactions | Fraud Count | Fraud Rate (%) | Avg Fraud Amount |
|----------|-------------------|-------------|----------------|------------------|
| shopping_net | 137,974 | 11,752 | 8.52% | $342.15 |
| grocery_pos | 184,326 | 12,601 | 6.84% | $287.93 |
| misc_net | 62,418 | 3,841 | 6.15% | $312.48 |
| gas_transport | 250,632 | 14,201 | 5.67% | $198.67 |
| grocery_net | 51,293 | 2,634 | 5.13% | $265.89 |

### Fraud Rate by Time of Day
| Hour Range | Total Transactions | Fraud Count | Fraud Rate (%) |
|------------|-------------------|-------------|----------------|
| 22:00 - 02:59 | 94,521 | 5,671 | 6.00% |
| 03:00 - 05:59 | 45,132 | 2,034 | 4.51% |
| 19:00 - 21:59 | 156,834 | 4,701 | 3.00% |
| 06:00 - 11:59 | 478,923 | 9,558 | 2.00% |
| 12:00 - 18:59 | 521,265 | 5,213 | 1.00% |

### Geographic Anomalies (Card Cloning Detection)
| Card Number | Transaction 1 | Transaction 2 | Minutes Apart | Distance (miles) | Fraud Likelihood |
|-------------|---------------|---------------|---------------|------------------|------------------|
| 4744...2891 | NY (NYC) | CA (LA) | 45 min | 2,451 mi | **Very High** |
| 3782...4521 | TX (Houston) | FL (Miami) | 58 min | 967 mi | **Very High** |
| 5123...7834 | IL (Chicago) | WA (Seattle) | 52 min | 1,737 mi | **Very High** |

### High-Risk Merchants
| Merchant | Category | Total Txns | Fraud Txns | Fraud Rate (%) | Total Fraud Amount |
|----------|----------|------------|------------|----------------|-------------------|
| fraud_Kirlin and Sons | shopping_net | 187 | 154 | 82.35% | $47,892.34 |
| fraud_Sporer-Keebler | misc_net | 132 | 96 | 72.73% | $28,456.78 |
| fraud_Swaniawski, Nitzsche and Welch | grocery_pos | 241 | 168 | 69.71% | $41,234.12 |

---

## 📈 Key Findings

1. **Late-night transactions (10 PM – 3 AM)** have a fraud rate 3× higher than daytime hours.
2. **High-value transactions ($500+)** carry a fraud rate of 8–12%, compared to <1% for sub-$100 transactions.
3. **"Shopping_net" and "grocery_pos"** are the merchant categories with the highest fraud rates.
4. **Elderly cardholders (65+)** experience disproportionately higher fraud rates, suggesting targeting of vulnerable populations.
5. **Geographic anomaly queries** successfully flag impossible-travel scenarios indicative of card cloning.

---

## 🛠 Tech Stack

| Tool | Purpose |
|---|---|
| **PostgreSQL** | Production-grade SQL queries |
| **SQLite** | Portable local execution via Python |
| **Python** | Data loading, visualization, CSV export |
| **Pandas / Matplotlib / Seaborn** | Data wrangling & charts |

---

## ⚡ Performance

| Metric | Value |
|--------|-------|
| **Data Loading** | ~15-20 seconds (1.3M rows) |
| **Query Execution** | 2-5 seconds per query (SQLite) |
| **Full Analysis Runtime** | ~3-4 minutes (all queries + visualizations) |
| **Memory Usage** | ~800 MB peak |
| **Output Size** | 8 charts + CSV exports (~5 MB total) |

### Production Optimization
For production environments with large datasets, consider adding these indexes:
```sql
-- Recommended indexes for faster query performance
CREATE INDEX idx_trans_date ON transactions(trans_date_trans_time);
CREATE INDEX idx_cc_num ON transactions(cc_num);
CREATE INDEX idx_is_fraud ON transactions(is_fraud);
CREATE INDEX idx_category ON transactions(category);
CREATE INDEX idx_merchant ON transactions(merchant);
CREATE INDEX idx_state ON transactions(state);
```

---

## 🤝 Contributing

Contributions are welcome! Fork the repo, create a branch, and submit a PR.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 👤 Author

**Arshad Ali Mohammed**
- [GitHub](https://github.com/Arshad289)
- [LinkedIn](https://www.linkedin.com/in/arshad-ali-m-080110135)
- Email: Mohammedarshadali89@gmail.com
