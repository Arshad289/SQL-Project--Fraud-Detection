# Dataset Description

## Source
**Simulated Credit Card Transaction Data** from Kaggle
https://www.kaggle.com/datasets/kartik2112/fraud-detection

## Download Instructions
1. Visit the Kaggle link above and download `fraudTrain.csv`.
2. Place it in the `data/` folder of this repository.
3. (Optional) Also download `fraudTest.csv` for validation.

## Overview
A simulated dataset of **1,296,675 credit card transactions** (training set) generated using the Sparkov data generation tool. Transactions span January 2019 to December 2020 across the United States, with a realistic ~0.6% fraud rate.

## Schema

| Column | Type | Description |
|---|---|---|
| `trans_date_trans_time` | timestamp | Date and time of the transaction |
| `cc_num` | bigint | Credit card number |
| `merchant` | string | Merchant name |
| `category` | string | Merchant category (grocery, gas, shopping, etc.) |
| `amt` | float | Transaction amount in USD |
| `first` | string | Cardholder first name |
| `last` | string | Cardholder last name |
| `gender` | char | Gender (M/F) |
| `street` | string | Cardholder street address |
| `city` | string | Cardholder city |
| `state` | string | Cardholder state (2-letter code) |
| `zip` | int | Cardholder ZIP code |
| `lat` | float | Cardholder latitude |
| `long` | float | Cardholder longitude |
| `city_pop` | int | Population of cardholder's city |
| `job` | string | Cardholder's occupation |
| `dob` | date | Cardholder date of birth |
| `trans_num` | string | Unique transaction identifier |
| `unix_time` | bigint | Unix timestamp of the transaction |
| `merch_lat` | float | Merchant latitude |
| `merch_long` | float | Merchant longitude |
| `is_fraud` | int | Fraud label (0 = legitimate, 1 = fraudulent) |

## Size
- **Training set:** ~1.3M rows, ~150 MB
- **Test set:** ~555K rows, ~65 MB
- **Columns:** 23

## Notes
- The dataset is synthetically generated and does not contain real personal information.
- Fraud rate is approximately 0.58%, reflecting realistic class imbalance.
- Ideal for practicing SQL-based fraud detection, anomaly detection, and pattern recognition.

## License
Publicly available on Kaggle for educational and research purposes.
