from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
import sys
import os

scripts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts'))
model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../model'))

for path in [scripts_path, model_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

from transform.transform_raw import transform_raw
from transform.transform_objects import transform_objects

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
}

dag = DAG(
    'transform',
    default_args=default_args,
    description='Преобразование сырых данных',
    schedule_interval=None,
    catchup=False,
)

transform_raw_task = PythonOperator(
    task_id='transform_raw',
    python_callable=transform_raw,
    dag=dag,
)

transform_objects_task = PythonOperator(
    task_id='transform_objects',
    python_callable=transform_objects,
    dag=dag,
)

trigger_load = TriggerDagRunOperator(
    task_id='trigger_load_dag',
    trigger_dag_id='load',
)

transform_raw_task >> transform_objects_task >> trigger_load