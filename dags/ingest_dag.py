from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'data_ingestion',
    default_args=default_args,
    description='Ingest and process e-commerce data',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['data', 'ingestion'],
) as dag:

    ingest_task = BashOperator(
        task_id='ingest_data',
        bash_command='cd /opt/airflow && python3 -m src.data.ingest',
    )