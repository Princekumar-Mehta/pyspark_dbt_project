# dbt Project — Silver to Gold Transformations

This sub-project contains the **dbt** data transformation models that power the **Gold layer** of the Medallion Architecture. It reads from the Silver Delta tables (produced by PySpark) and builds business-ready, aggregated analytical tables.

---

## Project Details

| Property | Value |
|---|---|
| **dbt Project Name** | `pyspark_dbt_airflow_internal` |
| **Version** | 1.0.0 |
| **Profile** | `default` |
| **Target Platform** | Databricks (Delta Lake) |

---

## Directory Structure

```
dbt_project/
├── models/
│   ├── silver/    # Staging/intermediate models reading from Silver Delta tables
│   └── gold/      # Final analytical models (business-ready)
├── analyses/      # Ad-hoc analytical SQL (not materialised)
├── macros/        # Reusable Jinja SQL macros
├── seeds/         # Static CSV seed data
├── snapshots/     # dbt snapshot definitions (SCD Type 2)
├── tests/         # Custom data quality tests
├── dbt_project.yml  # Project configuration
└── .gitignore
```

---

## Materialisation Strategy

Configured in `dbt_project.yml`:

| Layer | Schema | Materialisation |
|---|---|---|
| `silver` | `silver` | `table` |
| `gold` | `gold` | `table` |

Both layers are materialised as **Delta tables** in the `pyspark_dbt` catalog on Databricks.

---

## Data Flow

```
pyspark_dbt.silver.*          (produced by PySpark notebooks)
        │
        ▼
   dbt Silver models          (light staging / referencing Silver tables)
        │
        ▼
   dbt Gold models            (aggregated, business-ready analytical tables)
        │
        ▼
pyspark_dbt.gold.*
```

---

## Common Commands

```bash
# Run all models
dbt run

# Run only Gold layer models
dbt run --select gold

# Test data quality
dbt test

# Generate and serve documentation
dbt docs generate
dbt docs serve

# Clean compiled artifacts
dbt clean
```

---

## Prerequisites

1. **dbt-databricks** adapter installed:
   ```bash
   pip install dbt-databricks
   ```

2. **`profiles.yml`** configured (typically at `~/.dbt/profiles.yml`):
   ```yaml
   default:
     target: dev
     outputs:
       dev:
         type: databricks
         host: <your-workspace>.azuredatabricks.net
         http_path: /sql/1.0/warehouses/<warehouse-id>
         token: <your-pat-token>
         catalog: pyspark_dbt
         schema: gold
   ```

---

## Integration with Airflow

The `dbt_gold_layer_execution` DAG in `airflow_project/` automatically triggers this dbt project as part of the master medallion pipeline, after the PySpark Silver Transformation completes.