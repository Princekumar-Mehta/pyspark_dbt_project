from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime
import requests
import time

def run_dbt_build_and_wait():
    config = Variable.get("dbt_cloud_config", deserialize_json=True)
    token = str(config['token']).strip()
    account_id = str(config['account_id']).strip()
    job_id = str(config['job_id']).strip()
    
    base_url = f"https://xs752.us1.dbt.com/api/v2/accounts/{account_id}"
    headers = {
        "Authorization": f"Token {token}", 
        "Content-Type": "application/json"
    }

    # TRIGGER
    trigger_url = f"{base_url}/jobs/{job_id}/run/"
    response = requests.post(trigger_url, headers=headers, json={"cause": "Airflow Orchestration"})
    
    # FIX: Allow both 200 and 201
    if response.status_code not in [200, 201]:
        raise Exception(f"dbt API Error ({response.status_code}): {response.text}")
    
    run_id = response.json()['data']['id']
    print(f"Successfully triggered! Run ID: {run_id}")
    
    # POLLING (Wait for the job to finish)
    while True:
        status_res = requests.get(f"{base_url}/runs/{run_id}/", headers=headers).json()
        
        # We need the numeric status: 1=Queued, 2=Starting, 3=Running, 10=Success, 20=Error
        status = status_res['data']['status']
        status_label = status_res['data']['status_humanized']
        
        if status == 10: 
            print("dbt build COMPLETED SUCCESSFULLY.")
            break
        elif status in [20, 30]: 
            raise Exception(f"dbt build failed with status: {status_label}")
            
        print(f"Current dbt status: {status_label}... checking again in 30s")
        time.sleep(30)

with DAG(
    dag_id='dbt_gold_layer_execution',
    start_date=datetime(2026, 3, 24),
    schedule=None, # Triggered by parent or manual
    catchup=False
) as dag:

    dbt_task = PythonOperator(
        task_id='dbt_build_task',
        python_callable=run_dbt_build_and_wait
    )