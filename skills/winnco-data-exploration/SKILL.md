---
name: winnco-data-exploration
description: Use this skill to explore and validate the schemas and distributions of the WinnCo Parquet Lakehouse Data Dump using DuckDB.
---

# WinnCo Data Exploration Skill

This skill provides utilities to explore the local RealPage Parquet Lakehouse data. 

## Included Scripts

The scripts are located in `scripts/`:

### 1. Schema Search (`search_columns.py`)
This script uses DuckDB to scan all Parquet files in the Bronze, Dimension, and Fact tables for specific keyword matches in the column names.
*   **Usage:** Run this when you need to find where specific data (like emails, phone numbers, or addresses) lives across the entire Lakehouse schema.
*   **Command:** `python .agents/skills/winnco-data-exploration/scripts/search_columns.py`
*   **Customization:** Edit the `target_keywords` list inside the script to search for different column names.

### 2. Relational Uniqueness Verification (`check_bank_deposit.py`)
This script runs a complex DuckDB join across dimension and fact tables to verify if a given entity ID (like `LDTBankDepositNumber`) is unique to a single resident or shared across multiple residents.
*   **Usage:** Run this when you need to determine if a dimension attribute is a unique identifier (suitable for a Graph Node/Edge) or a batch grouping identifier.
*   **Command:** `python .agents/skills/winnco-data-exploration/scripts/check_bank_deposit.py`

## Instructions for Agents
1. Before assuming a column implies uniqueness (e.g., assuming a deposit number equals a single bank account), run the uniqueness verification script to prove it.
2. If the user asks where a piece of data is stored, do not guess. Run the `search_columns.py` script.
