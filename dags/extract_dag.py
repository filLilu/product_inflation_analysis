from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../scripts'))

from extract.extract_food_inflation import extract

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
}

dag = DAG(
    'extract',
    default_args=default_args,
    description='Извлечение данных из Worldbank с помощью API',
    schedule_interval=None,
    catchup=False,
)

extract_task = PythonOperator(
    task_id='extract_food_inflation',
    python_callable=extract,
    dag=dag,
)

trigger_transform = TriggerDagRunOperator(
    task_id='trigger_transform_dag',
    trigger_dag_id='transform',
)

extract_task >> trigger_transform