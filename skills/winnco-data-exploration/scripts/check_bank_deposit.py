import duckdb
from pathlib import Path

# Connect to in-memory duckdb
conn = duckdb.connect()

# Paths
base_dir = r"c:/Users/Int202613/Documents/Github/WinnCo/WinnCo Dataset/Data Dump"
dim_ta = f"{base_dir}/dim_tables/dim_transaction_activity.parquet"
fact_ta = f"{base_dir}/fact_tables/fact_transaction_activity.parquet"

print("Running query...")

# Query: How many distinct ResidentHouseHoldIDs are there per LDTBankDepositNumber?
query = f"""
SELECT 
    d.LDTBankDepositNumber, 
    COUNT(DISTINCT f.osl_ResidentHouseHoldID) as unique_residents,
    COUNT(f.TAKey) as total_transactions
FROM read_parquet('{dim_ta}') d
JOIN read_parquet('{fact_ta}') f ON d.TAKey = f.TAKey
WHERE d.LDTBankDepositNumber IS NOT NULL AND d.LDTBankDepositNumber != 0
GROUP BY d.LDTBankDepositNumber
ORDER BY unique_residents DESC
LIMIT 10;
"""

print(conn.execute(query).df().to_string())

# Also check how many total LDTBankDepositNumbers exist and how many have > 1 unique resident
summary_query = f"""
WITH stats AS (
    SELECT 
        d.LDTBankDepositNumber, 
        COUNT(DISTINCT f.osl_ResidentHouseHoldID) as unique_residents
    FROM read_parquet('{dim_ta}') d
    JOIN read_parquet('{fact_ta}') f ON d.TAKey = f.TAKey
    WHERE d.LDTBankDepositNumber IS NOT NULL AND d.LDTBankDepositNumber != 0
    GROUP BY d.LDTBankDepositNumber
)
SELECT 
    COUNT(*) as total_deposit_numbers,
    SUM(CASE WHEN unique_residents > 1 THEN 1 ELSE 0 END) as numbers_with_multiple_residents,
    MAX(unique_residents) as max_residents_per_number
FROM stats;
"""

print("\nSummary:")
print(conn.execute(summary_query).df().to_string())
