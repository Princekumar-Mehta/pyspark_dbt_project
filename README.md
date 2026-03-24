# PySpark + dbt + Airflow Medallion Pipeline

An end-to-end data engineering monorepo implementing a **Medallion Architecture** (Bronze → Silver → Gold) using **Apache Spark (Databricks)**, **dbt**, and **Apache Airflow** for orchestration.

---

## Architecture Overview

```
Source Data (CSV)
      │
      ▼
┌─────────────────────────────────────────────────┐
│              BRONZE LAYER (Databricks)           │
│  PySpark Structured Streaming → Delta Tables     │
│  Entities: customers, payments, locations,       │
│            vehicles, drivers, trips              │
└─────────────────────────┬───────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────┐
│              SILVER LAYER (Databricks)           │
│  PySpark Batch Transformations → Delta Tables    │
│  Deduplication, Upserts, Data Cleansing          │
└─────────────────────────┬───────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────┐
│               GOLD LAYER (dbt)                   │
│  SQL Transformations → Analytical Tables         │
│  Business-ready aggregated models                │
└─────────────────────────┬───────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────┐
│          ORCHESTRATION (Apache Airflow)          │
│  Master DAG → triggers Databricks & dbt runs    │
└─────────────────────────────────────────────────┘
```

---

## Repository Structure

```
pyspark_dbt_project/
├── airflow_project/       # Apache Airflow orchestration (Dockerized)
├── dbt_project/           # dbt transformations (Silver → Gold layer)
├── pyspark/               # Databricks PySpark notebooks (Bronze & Silver)
└── README.md              # This file
```

---

## Sub-Projects

| Sub-Project | Description |
|---|---|
| [`airflow_project/`](./airflow_project/README.md) | Dockerized Airflow 3.x setup with CeleryExecutor, production DAGs, and Databricks integration |
| [`dbt_project/`](./dbt_project/README.md) | dbt project for Silver → Gold model transformations on Databricks |
| [`pyspark/`](./pyspark/README.md) | Databricks PySpark notebooks for Bronze ingestion and Silver transformation |

---

## Data Pipeline Flow

1. **Bronze Ingestion** — Raw CSV files are streamed into Delta tables using PySpark Structured Streaming on Databricks.
2. **Silver Transformation** — Bronze Delta tables are cleaned, deduped, and upserted into the Silver layer via PySpark batch jobs.
3. **Gold Transformation** — dbt SQL models aggregate and join Silver tables into business-ready Gold tables.
4. **Orchestration** — Airflow's `master_medallion_pipeline` DAG ties the entire pipeline together, sequentially triggering Databricks and dbt jobs.

---

## Entities

The pipeline processes a ride-hailing domain dataset with the following entities:

- `customers`
- `drivers`
- `vehicles`
- `trips`
- `payments`
- `locations`

---

## Prerequisites

- **Docker & Docker Compose** (for Airflow)
- **Databricks** workspace with Serverless compute or an active cluster
- **dbt-databricks** adapter configured with a `profiles.yml`
- Python 3.11+

---

## Quick Start

1. **Start Airflow**:
   ```bash
   cd airflow_project
   docker compose up -d
   ```

2. **Configure Databricks connection** in the Airflow UI (Connection ID: `databricks_default`).

3. **Trigger the master pipeline DAG** (`master_medallion_pipeline`) from the Airflow UI or CLI:
   ```bash
   airflow dags trigger master_medallion_pipeline
   ```

4. **Run dbt models manually** (optional):
   ```bash
   cd dbt_project
   dbt run
   dbt test
   ```
