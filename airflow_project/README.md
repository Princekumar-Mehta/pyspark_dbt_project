# Airflow Project

Dockerized **Apache Airflow 3.x** orchestration layer for the PySpark + dbt Medallion pipeline. Uses **CeleryExecutor** with Redis and PostgreSQL backends.

---

## Directory Structure

```
airflow_project/
├── dags/                              # All DAG definitions
│   ├── prod_dag_master_medallion.py   # Master pipeline orchestrator
│   ├── prod_dag_databricks_pyspark_trigger.py   # Triggers Bronze ingestion on Databricks
│   ├── prod_dag_databricks_dbt_trigger.py       # Triggers dbt Gold layer on Databricks
│   ├── dag_orchestrate_parent.py      # DAG-to-DAG orchestration examples
│   ├── dag_orchestrate_1.py           # Sub-DAG example 1
│   ├── dag_orchestrate_2.py           # Sub-DAG example 2
│   ├── 1_first_dag.py                 # Learning: Basic DAG
│   ├── 2_dag_versioning.py            # Learning: DAG versioning
│   ├── 3_operators.py                 # Learning: Operators
│   ├── 4_xcoms_auto.py                # Learning: XComs (auto)
│   ├── 5_xcoms_kwargs.py              # Learning: XComs (kwargs)
│   ├── 6_parallel_tasks.py            # Learning: Parallel tasks
│   ├── 7_branches.py                  # Learning: BranchPythonOperator
│   ├── 8_schedule_preset.py           # Learning: Schedule presets
│   ├── 9_schedule_cron.py             # Learning: Cron schedules
│   ├── 10_schedule_delta.py           # Learning: Timedelta schedules
│   ├── 11_incremental_load.py         # Learning: Incremental data loading
│   ├── 12_special_dates_schedule.py   # Learning: Special-date scheduling
│   ├── 13_asset.py                    # Learning: Airflow Assets
│   └── 14_asset_dependent.py          # Learning: Asset-dependent DAGs
├── config/
│   └── airflow.cfg                    # Custom Airflow configuration file
├── plugins/                           # Custom Airflow plugins
├── logs/                              # Airflow task logs (Docker volume)
├── docker-compose.yaml                # Full Airflow stack definition
├── .env                               # Environment variables
├── pyproject.toml                     # Python project config (uv/pip)
└── main.py                            # Entry point (local testing helper)
```

---

## Production DAGs

### `master_medallion_pipeline`
The root orchestrator. Sequentially triggers the two downstream pipelines:

```
trigger_databricks_ingestion  ──►  trigger_dbt_gold_snapshots
```

- **Step 1 — Databricks PySpark** (`trigger_bronze_ingestion_final`): Runs the Bronze ingestion notebook on Databricks Serverless.
- **Step 2 — dbt Gold Layer** (`dbt_gold_layer_execution`): Runs dbt models for the Gold layer.

### `trigger_bronze_ingestion_final`
Uses the `DatabricksHook` to submit a one-off notebook run via the Databricks Jobs API (`2.1/jobs/runs/submit`).

- **Notebook**: `/Workspace/pyspark_dbt_project/bronze_ingestion`
- **Connection**: `databricks_default` (configured in Airflow Connections)

### `dbt_gold_layer_execution`
Triggers a **dbt Cloud job** via the dbt Cloud REST API. It:
1. Reads `account_id`, `job_id`, and `token` from an Airflow Variable (`dbt_cloud_config`).
2. POSTs to the dbt Cloud API to trigger the job.
3. **Polls every 30 seconds** until the job succeeds (status `10`) or fails (status `20/30`).

This runs the dbt Silver incremental model and Gold SCD Type 2 snapshots on dbt Cloud.

---

## Docker Services

| Service | Image | Port | Role |
|---|---|---|---|
| `postgres` | postgres:16 | 5433 | Airflow metadata database |
| `redis` | redis:7.2-bookworm | 6379 | Celery broker |
| `airflow-apiserver` | apache/airflow:3.1.8 | 8080 | REST API + Airflow UI |
| `airflow-scheduler` | apache/airflow:3.1.8 | — | DAG scheduling |
| `airflow-dag-processor` | apache/airflow:3.1.8 | — | DAG file parsing |
| `airflow-worker` | apache/airflow:3.1.8 | — | Celery task execution |
| `airflow-triggerer` | apache/airflow:3.1.8 | — | Async/deferrable operators |
| `flower` *(optional)* | apache/airflow:3.1.8 | 5555 | Celery monitoring UI |

---

## Getting Started

### 1. Prerequisites
- Docker & Docker Compose installed
- At least **4 GB RAM** and **2 CPUs** available for Docker

### 2. Set environment variables

Create or edit `.env` in this directory:
```env
AIRFLOW_UID=50000
AIRFLOW__API_AUTH__JWT_SECRET=your_jwt_secret
AIRFLOW__API_AUTH__JWT_ISSUER=airflow
```

### 3. Start the stack

```bash
docker compose up -d
```

### 4. Access the Airflow UI

Open [http://localhost:8080](http://localhost:8080) in your browser.

Default credentials:
- **Username**: `airflow`
- **Password**: `airflow`

### 5. Configure Databricks Connection

In the Airflow UI → **Admin → Connections**, create:
- **Conn ID**: `databricks_default`
- **Conn Type**: `Databricks`
- **Host**: `https://<your-workspace>.azuredatabricks.net` (or AWS/GCP equivalent)
- **Token**: Your Databricks Personal Access Token

### 6. Trigger the pipeline

```bash
docker compose exec airflow-scheduler airflow dags trigger master_medallion_pipeline
```

---

## Stopping the Stack

```bash
docker compose down
```

To also remove volumes (database data):
```bash
docker compose down -v
```
