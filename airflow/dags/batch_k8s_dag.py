from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.operators.python import BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

def run_weekly(**context):
    if datetime.strptime(context['ds'], "%Y-%m-%d").weekday() == 6:
        return "mlib_evaluate"
    return "skip_mlib"

with DAG(
    dag_id="batch_k8s_dag",
    default_args=default_args,
    description="Batch layer DAG trên Kubernetes (Minikube)",
    schedule_interval="@daily",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    max_active_runs=1,
) as dag:

    crawler_task = KubernetesPodOperator(
        task_id="crawler_batch",
        name="crawler-batch",
        namespace="default",
        image="crawler:latest",
        cmds=["python", "main.py"],
        get_logs=True,
    )

    kafka_to_hdfs_ohlcv_task = KubernetesPodOperator(
        task_id="kafka_to_hdfs_ohlcv",
        name="kafka-to-hdfs-ohlcv",
        namespace="default",
        image="kafka_to_hdfs_ohlcv:latest",
        cmds=["python", "main.py"],
        get_logs=True,
    )

    kafka_to_hdfs_market_task = KubernetesPodOperator(
        task_id="kafka_to_hdfs_market",
        name="kafka-to-hdfs-market",
        namespace="default",
        image="kafka_to_hdfs_market:latest",
        cmds=["python", "main.py"],
        get_logs=True,
    )

    daily_ohlcv_task = KubernetesPodOperator(
        task_id="daily_ohlcv",
        name="daily-ohlcv",
        namespace="default",
        image="daily_ohlcv:latest",
        cmds=["spark-submit"],
        arguments=[
            "--master", "spark://spark-master:7077",
            "--packages", "org.elasticsearch:elasticsearch-spark-30_2.12:8.11.0",
            "--conf", "spark.jars.ivy=/tmp/.ivy2",
            "daily_ohlcv.py"
        ],
        get_logs=True,
    )

    analyst_ohlcv_task = KubernetesPodOperator(
        task_id="analyst_ohlcv",
        name="analyst-ohlcv",
        namespace="default",
        image="analyst_ohlcv:latest",
        cmds=["python", "main.py"],
        get_logs=True,
    )

    branch_task = BranchPythonOperator(
        task_id="branch_mlib",
        python_callable=run_weekly,
        provide_context=True,
    )

    skip_mlib = DummyOperator(task_id="skip_mlib")

    mlib_evaluate_task = KubernetesPodOperator(
        task_id="mlib_evaluate",
        name="mlib-evaluate",
        namespace="default",
        image="mlib_evaluate:latest",
        cmds=["python", "main.py"],
        get_logs=True,
    )

    crawler_task >> [kafka_to_hdfs_ohlcv_task, kafka_to_hdfs_market_task]
    kafka_to_hdfs_ohlcv_task >> daily_ohlcv_task >> analyst_ohlcv_task
    daily_ohlcv_task >> branch_task
    branch_task >> [mlib_evaluate_task, skip_mlib]
