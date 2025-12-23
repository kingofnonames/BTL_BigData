from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.python import BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta
def run_weekly(**context):
    """
    Chỉ chạy ML Evaluate nếu là chủ nhật
    weekday(): 0 = Monday ... 6 = Sunday
    """
    if datetime.strptime(context['ds'], "%Y-%m-%d").weekday() == 6:
        return "mlib_evaluate"
    return "skip_mlib"
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="batch_docker_dag",
    default_args=default_args,
    description="Batch layer DAG với crawler, Kafka, daily, analyst và ML Evaluate (chỉ tuần 1 lần)",
    schedule_interval="@daily",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    max_active_runs=1,
) as dag:

    crawler_task = DockerOperator(
        task_id="crawler_batch",
        image="crawler:latest",
        docker_url="npipe:////./pipe/docker_engine",
        network_mode="docker-deployment_bigdata-net",
        auto_remove=True,
        command="python main.py",
    )

    kafka_to_hdfs_ohlcv_task = DockerOperator(
        task_id="kafka_to_hdfs_ohlcv",
        image="kafka_to_hdfs_ohlcv:latest",
        docker_url="npipe:////./pipe/docker_engine",
        network_mode="docker-deployment_bigdata-net",
        auto_remove=True,
        command="python main.py",
    )

    kafka_to_hdfs_market_task = DockerOperator(
        task_id="kafka_to_hdfs_market",
        image="kafka_to_hdfs_market:latest",
        docker_url="npipe:////./pipe/docker_engine",
        network_mode="docker-deployment_bigdata-net",
        auto_remove=True,
        command="python main.py",
    )

    daily_ohlcv_task = DockerOperator(
        task_id="daily_ohlcv",
        image="daily_ohlcv:latest",
        docker_url="npipe:////./pipe/docker_engine",
        network_mode="docker-deployment_bigdata-net",
        auto_remove=True,
        command="spark-submit --master spark://spark-master:7077 "
                "--packages org.elasticsearch:elasticsearch-spark-30_2.12:8.11.0 "
                "--conf spark.jars.ivy=/tmp/.ivy2 daily_ohlcv.py",
    )

    analyst_ohlcv_task = DockerOperator(
        task_id="analyst_ohlcv",
        image="analyst_ohlcv:latest",
        docker_url="npipe:////./pipe/docker_engine",
        network_mode="docker-deployment_bigdata-net",
        auto_remove=True,
        command="python main.py",
    )

    branch_task = BranchPythonOperator(
        task_id="branch_mlib",
        python_callable=run_weekly,
        provide_context=True,
    )

    skip_mlib = DummyOperator(task_id="skip_mlib")

    mlib_evaluate_task = DockerOperator(
        task_id="mlib_evaluate",
        image="mlib_evaluate:latest",
        docker_url="npipe:////./pipe/docker_engine",
        network_mode="docker-deployment_bigdata-net",
        auto_remove=True,
        command="python main.py",
        execution_timeout=timedelta(days=1),
    )

    crawler_task >> [kafka_to_hdfs_ohlcv_task, kafka_to_hdfs_market_task]
    kafka_to_hdfs_ohlcv_task >> daily_ohlcv_task >> analyst_ohlcv_task
    daily_ohlcv_task >> branch_task
    branch_task >> [mlib_evaluate_task, skip_mlib]
