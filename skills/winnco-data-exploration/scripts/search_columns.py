import duckdb
from pathlib import Path

base_dir = Path("/Users/prabath/Downloads/WinnCo/WinnCo Dataset/Data Dump")
conn = duckdb.connect()

target_keywords = ['email', 'phone', 'website', 'address', 'city', 'state', 'zip']

results = []

for pdir in ['bronze_tables', 'dim_tables', 'fact_tables']:
    dir_path = base_dir / pdir
    if dir_path.exists():
        for pfile in dir_path.glob("*.parquet"):
            try:
                # get schema
                schema_df = conn.execute(f"DESCRIBE SELECT * FROM read_parquet('{pfile}')").df()
                for col in schema_df['column_name']:
                    col_lower = col.lower()
                    if any(k in col_lower for k in target_keywords):
                        results.append(f"{pdir}/{pfile.name} -> {col}")
            except Exception as e:
                pass

print("Found matching columns:")
for r in sorted(results):
    print(r)
