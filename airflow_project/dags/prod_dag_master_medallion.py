from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime

with DAG(
    dag_id='master_medallion_pipeline',
    start_date=datetime(2026, 3, 24),
    catchup=False,
    tags=['production', 'medallion']
) as dag:

    # 1. Trigger Databricks (Bronze/Silver Ingestion)
    trigger_databricks = TriggerDagRunOperator(
        task_id='trigger_databricks_ingestion',
        trigger_dag_id='trigger_bronze_ingestion_final', # Must match the dag_id in your Databricks file
        wait_for_completion=True,
        poke_interval=30
    )

    # 2. Trigger dbt (Silver/Gold Transformations)
    trigger_dbt = TriggerDagRunOperator(
        task_id='trigger_dbt_gold_snapshots',
        trigger_dag_id='dbt_gold_layer_execution', # Matches the DAG we just fixed
        wait_for_completion=True,
        poke_interval=30
    )

    # Define the Dependency
    trigger_databricks >> trigger_dbt