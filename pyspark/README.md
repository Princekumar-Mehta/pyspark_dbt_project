# PySpark — Databricks Notebooks

This sub-project contains **Databricks PySpark notebooks** responsible for the **Bronze** and **Silver** layers of the Medallion Architecture.

---

## Contents

```
pyspark/
├── bronze_ingestion.ipynb       # Spark Structured Streaming → Bronze Delta tables
└── silver_transformation.ipynb  # Batch transformations → Silver Delta tables
```

---

## Notebooks

### `bronze_ingestion.ipynb` — Bronze Layer

Ingests raw CSV files from Databricks Volumes into Bronze Delta tables using **PySpark Structured Streaming**.

**Entities processed:**
- `customers`, `payments`, `locations`, `vehicles`, `drivers`, `trips`

**How it works:**
1. Reads the schema of each entity using a batch read from `/Volumes/pyspark_dbt/source/source_data/{entity}/{entity}.csv`.
2. Opens a streaming read over the entire source folder.
3. Writes the stream to a Delta table `pyspark_dbt.bronze.{entity}` in **append** mode with a checkpoint location at `/Volumes/pyspark_dbt/bronze/checkpoint/{entity}`.
4. Uses `.trigger(once=True)` for a one-shot micro-batch execution.

---

### `silver_transformation.ipynb` — Silver Layer

Applies **batch transformations** to the Bronze Delta tables and upserts the results into the Silver layer.

**Entities processed:** `customers`, `drivers`, `locations`, `payments`, `vehicles`

**Transformations applied (via `Transformations` class):**

| Method | Description |
|---|---|
| `dedup()` | Deduplicates rows using a window function ordered by a CDC timestamp column |
| `process_timestamp()` | Adds a `process_timestamp` column with the current ingestion time |
| `upsert()` | Performs a Delta Lake `MERGE` (update matched + insert new) keyed on entity ID columns |

**Entity-specific cleansing:**

| Entity | Specific Transformations |
|---|---|
| `customers` | Extracts `email_domain`, normalises `phone_number`, combines `first_name`+`last_name` → `full_name` |
| `drivers` | Normalises `phone_number`, combines name fields into `full_name` |
| `locations` | Deduplication only |
| `payments` | Derives `online_payment_status` from `payment_method` and `payment_status` |
| `vehicles` | Uppercases `make` field |

---

## Infrastructure

| Resource | Path / Name |
|---|---|
| Source CSV Volumes | `/Volumes/pyspark_dbt/source/source_data/{entity}/` |
| Bronze Delta tables | `pyspark_dbt.bronze.{entity}` |
| Silver Delta tables | `pyspark_dbt.silver.{entity}` |
| Checkpoint location | `/Volumes/pyspark_dbt/bronze/checkpoint/{entity}` |

---

## How to Run

These notebooks are designed to be executed on **Databricks** (Serverless or classic cluster).

- **Manually**: Open the notebooks in Databricks Workspace and click **Run All**.
- **Via Airflow**: The `trigger_bronze_ingestion_final` DAG in `airflow_project` triggers these notebooks automatically through the Databricks Jobs API.
