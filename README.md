# PySpark + dbt + Airflow Medallion Pipeline

An end-to-end data engineering monorepo implementing a **Medallion Architecture** (Bronze → Silver → Gold) using **Apache Spark (Databricks)**, **dbt**, and **Apache Airflow** for orchestration.

---

## Architecture Overview

```
Source Data (CSV on Databricks Volumes)
          │
          ▼
┌──────────────────────────────────────────────────────┐
│                 BRONZE LAYER  (PySpark)               │
│  Structured Streaming → Delta Tables                  │
│  Entities: customers, drivers, vehicles,              │
│            payments, locations, trips                 │
└────────┬─────────────────────────────────┬───────────┘
         │  5 entities                     │  trips
         ▼                                ▼
┌─────────────────────┐       ┌───────────────────────┐
│   SILVER  (PySpark) │       │   SILVER (dbt)        │
│  Batch dedup, CDC   │       │  Incremental model    │
│  upsert via MERGE   │       │  with watermark logic │
│  pyspark_dbt.silver │       │  pyspark_dbt.silver   │
└─────────┬───────────┘       └──────────┬────────────┘
          │                              │
          └─────────────┬────────────────┘
                        ▼
┌──────────────────────────────────────────────────────┐
│                  GOLD LAYER  (dbt)                    │
│  SCD Type 2 Snapshots → Historized Dimension Tables  │
│  dim_customers, dim_drivers, dim_vehicles,            │
│  dim_payments, dim_locations, fact_trips              │
│  pyspark_dbt.gold                                    │
└──────────────────────┬───────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────┐
│             ORCHESTRATION  (Apache Airflow)           │
│  CeleryExecutor on Docker — Master DAG triggers       │
│  Databricks PySpark jobs → dbt snapshot runs         │
└──────────────────────────────────────────────────────┘
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

1. **Bronze Ingestion (PySpark)** — All 6 entities are streamed from CSV Volumes into Delta tables using PySpark Structured Streaming on Databricks.
2. **Silver Transformation (PySpark)** — 5 entities (`customers`, `drivers`, `vehicles`, `payments`, `locations`) are cleaned, deduped, and upserted via Delta Lake MERGE using PySpark batch jobs.
3. **Silver — Trips (dbt)** — The `trips` entity is modelled as a dbt **incremental model** with CDC high-watermark logic, reading directly from the Bronze Delta table.
4. **Gold Layer (dbt Snapshots)** — dbt **SCD Type 2 snapshots** build historized dimension and fact tables (`dim_customers`, `dim_drivers`, `dim_vehicles`, `dim_payments`, `dim_locations`, `fact_trips`) in the `pyspark_dbt.gold` schema.
5. **Orchestration (Airflow)** — The `master_medallion_pipeline` DAG sequentially triggers the Databricks PySpark jobs and the dbt snapshot runs via CeleryExecutor on Docker.

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
