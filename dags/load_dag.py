from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import sys
import os

scripts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts'))
model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../model'))

for path in [scripts_path, model_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

from load.load_stg import load_stg
from load.load_core import load_core

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
}

dag = DAG(
    'load',
    default_args=default_args,
    description='Загрузка данных в хранилище',
    schedule_interval=None,
    catchup=False,
)

load_stg_task = PythonOperator(
    task_id='load_stg',
    python_callable=load_stg,
    dag=dag,
)

load_core_task = PythonOperator(
    task_id='load_core',
    python_callable=load_core,
    dag=dag,
)

load_stg_task >> load_core_task