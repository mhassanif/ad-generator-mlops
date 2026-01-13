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
    'model_training',
    default_args=default_args,
    description='Train T5 model for ad generation',
    schedule_interval=timedelta(days=7),  # Run weekly
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['model', 'training', 'ml'],
) as dag:

    train_task = BashOperator(
        task_id='train_model',
        bash_command='cd /opt/airflow && python3 -m src.models.train --epochs 3',
    )