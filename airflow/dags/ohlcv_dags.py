from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'bigdata_pipeline',
    default_args=default_args,
    description='Pipeline for BigData project',
    schedule_interval='0 2 * * *',
    start_date=datetime(2025, 1, 1),
    catchup=False
)

crawler_task = KubernetesPodOperator(
    namespace='bigdata',
    image='crawler:latest',
    cmds=["python", "main.py"],
    name='crawler-job',
    task_id='crawler_task',
    get_logs=True,
    dag=dag
)

daily_ohlcv_task = KubernetesPodOperator(
    namespace='bigdata',
    image='daily_ohlcv:latest',
    cmds=["spark-submit",
          "--master", "spark://spark-master:7077",
          "--packages", "org.elasticsearch:elasticsearch-spark-30_2.12:8.11.0",
          "--conf", "spark.jars.ivy=/tmp/.ivy2",
          "daily_ohlcv.py"],
    name='daily-ohlcv-job',
    task_id='daily_ohlcv_task',
    get_logs=True,
    dag=dag
)

analyst_ohlcv_task = KubernetesPodOperator(
    namespace='bigdata',
    image='analyst_ohlcv:latest',
    cmds=["spark-submit",
          "--master", "spark://spark-master:7077",
          "--packages", "org.elasticsearch:elasticsearch-spark-30_2.12:8.11.0",
          "--conf", "spark.jars.ivy=/tmp/.ivy2",
          "analyst_ohlcv.py"],
    name='analyst-ohlcv-job',
    task_id='analyst_ohlcv_task',
    get_logs=True,
    dag=dag
)

crawler_task >> [daily_ohlcv_task, analyst_ohlcv_task]
