from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.databricks.hooks.databricks import DatabricksHook
from datetime import datetime

def trigger_databricks_run():
    hook = DatabricksHook(databricks_conn_id='databricks_default')
    
    payload = {
        "tasks": [
            {
                "task_key": "bronze_ingestion_task",
                "notebook_task": {
                    "notebook_path": "/Workspace/pyspark_dbt_project/bronze_ingestion",
                    "source": "WORKSPACE"
                }
            }
        ]
    }
    
    # Note: When you use the 'tasks' array, the Free Tier/Serverless 
    # automatically assumes serverless compute if no cluster is provided.
    response = hook._do_api_call(('POST', '2.1/jobs/runs/submit'), payload)
    print(f"Triggered Run ID: {response.get('run_id')}")
# def trigger_databricks_run():
#     hook = DatabricksHook(databricks_conn_id='databricks_default')
    
#     # Use the /Workspace prefix you just found
#     notebook_path = "/Workspace/pyspark_dbt_project/bronze_ingestion" 

#     payload = {
#         "tasks": [
#             {
#                 "task_key": "bronze_task",
#                 "notebook_task": {
#                     "notebook_path": notebook_path,
#                     "source": "WORKSPACE"
#                 },
#                 "environment_key": "Default" 
#             }
#         ],
#         "environments": [
#             {
#                 "environment_key": "Default",
#                 "spec": {
#                     "client": "serverless"
#                 }
#             }
#         ]
#     }
    
#     # Triggering the run
#     response = hook._do_api_call(('POST', '2.1/jobs/runs/submit'), payload)
#     print(f"Triggered Run ID: {response.get('run_id')}")

with DAG(
    dag_id='trigger_bronze_ingestion_final',
    start_date=datetime(2026, 3, 24),
    schedule=None,
    catchup=False
) as dag:

    run_notebook = PythonOperator(
        task_id='manual_api_trigger',
        python_callable=trigger_databricks_run
    )