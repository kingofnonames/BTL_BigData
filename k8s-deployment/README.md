<!-- BTL_BigData Kubernetes Deployment
1️⃣ Yêu cầu

Minikube đã cài và đang chạy.

Docker Desktop hoặc Docker daemon đang chạy.

Các Docker images cho các job đã build sẵn.

Thư mục dữ liệu tồn tại:

./data/hdfs/namenode
./data/hdfs/datanode
./data/elasticsearch
./airflow/dags
./airflow/logs

2️⃣ Cấu trúc thư mục
k8s-deployment/
├── configmap # Chứa các ConfigMap cho env variables
├── secrets # Chứa các Secret (credentials)
├── deployments # Chứa các Deployment YAML
├── jobs # Chứa các Job YAML (batch jobs)
└── services # Chứa các Service YAML để pod kết nối

3️⃣ Sử dụng Docker daemon của Minikube

Nếu muốn build Docker image trực tiếp trong Minikube, chạy:

eval $(minikube -p minikube docker-env)

4️⃣ Build Docker images

Ví dụ các job Spark/Python:

# analyst_ohlcv

docker build -t analyst_ohlcv:latest ./path_to_analyst_ohlcv

# daily_ohlcv

docker build -t daily_ohlcv:latest ./path_to_daily_ohlcv

# kafka_to_hdfs_ohlcv

docker build -t kafka_to_hdfs_ohlcv:latest ./path_to_kafka_to_hdfs_ohlcv

# kafka_to_hdfs_market

docker build -t kafka_to_hdfs_market:latest ./path_to_kafka_to_hdfs_market

# mlib_evaluate

docker build -t mlib_evaluate:latest ./path_to_mlib_evaluate

# ohlcv_speed

docker build -t ohlcv_speed:latest ./path_to_ohlcv_speed

# speed_crawler

docker build -t speed_crawler:latest ./path_to_speed_crawler

5️⃣ Apply ConfigMap và Secret
kubectl apply -f configmap/bigdata-config.yaml
kubectl apply -f secrets/airflow-secret.yaml

ConfigMap chứa HDFS_PATH, Kafka bootstrap, Elasticsearch host/index, v.v.
Secret chứa credentials (nếu có, ví dụ PostgreSQL cho Airflow).

6️⃣ Deploy Services
kubectl apply -f services/

Services giúp các pod trong namespace bigdata kết nối với nhau.

7️⃣ Deploy Core Deployments
kubectl apply -f deployments/

Bao gồm:

Zookeeper & Kafka

HDFS Namenode & Datanode

Spark Master & Worker

Elasticsearch & Kibana

Airflow DB, Webserver, Scheduler

8️⃣ Deploy Jobs / Batch Jobs
kubectl apply -f jobs/

Bao gồm các job:

analyst_ohlcv

daily_ohlcv

mlib_evaluate

kafka_to_hdfs_ohlcv

kafka_to_hdfs_market

ohlcv_speed

speed_crawler

Jobs sẽ chạy 1 lần và kết thúc. Nếu muốn chạy lại:

kubectl delete job <job-name> -n bigdata
kubectl apply -f jobs/<job-yaml>

9️⃣ Kiểm tra trạng thái

# Kiểm tra pods

kubectl get pods -n bigdata

# Kiểm tra services

kubectl get svc -n bigdata

# Xem logs của pod

kubectl logs <pod-name> -n bigdata

🔟 Truy cập Web UI

Airflow Webserver: http://<minikube-ip>:8080

Spark Master UI: http://<minikube-ip>:8080

Elasticsearch: http://<minikube-ip>:9200

Kibana: http://<minikube-ip>:5601

Lấy Minikube IP:

minikube ip

1️⃣1️⃣ Debug & Ghi chú

Sửa ConfigMap nếu cần thay đổi HDFS path, Kafka topic, Elasticsearch index:

kubectl edit configmap bigdata-config -n bigdata

Xem chi tiết pod:

kubectl describe pod <pod-name> -n bigdata

Nếu pod không chạy, kiểm tra logs:

kubectl logs <pod-name> -n bigdata

HostPath volumes sẽ mount dữ liệu từ máy local; đảm bảo các thư mục dữ liệu tồn tại trước khi deploy. -->

BTL_BigData Kubernetes Deployment

1. Yêu cầu

Minikube đã được cài đặt và đang chạy.

Docker Desktop hoặc Docker daemon đang chạy.

Helm (tùy chọn, nếu dùng chart để quản lý).

Spark, Kafka, HDFS, Elasticsearch, Airflow được triển khai qua Docker images đã build sẵn. (docker-compose.yml trong thư mục docker-deployment (docker-compose up -d))

2. Cấu trúc thư mục
   k8s-deployment/
   ├── configmap # Chứa các ConfigMap cho env variables
   ├── secrets # Chứa các Secret (ví dụ credentials)
   ├── deployments # Chứa các Deployment YAML
   ├── jobs # Chứa các Job YAML (batch jobs)
   └── services # Chứa các Service YAML để pod kết nối

3. Build Docker images cho các job

Đi vào thư mục chứa Dockerfile của từng job và build:

# Ví dụ: build analyst_ohlcv

docker build -t analyst_ohlcv:latest ./path_to_analyst_ohlcv

# Build daily_ohlcv

docker build -t daily_ohlcv:latest ./path_to_daily_ohlcv

# Build kafka_to_hdfs_ohlcv

docker build -t kafka_to_hdfs_ohlcv:latest ./path_to_kafka_to_hdfs_ohlcv

# Build kafka_to_hdfs_market

docker build -t kafka_to_hdfs_market:latest ./path_to_kafka_to_hdfs_market

# Build mlib_evaluate

docker build -t mlib_evaluate:latest ./path_to_mlib_evaluate

# Build ohlcv_speed

docker build -t ohlcv_speed:latest ./path_to_ohlcv_speed

# Build speed_crawler

docker build -t speed_crawler:latest ./path_to_speed_crawler

Nếu dùng Minikube Docker daemon, chạy trước:

eval $(minikube -p minikube docker-env)

4. Deploy ConfigMap và Secrets
   kubectl apply -f configmap/bigdata-config.yaml
   kubectl apply -f secrets/airflow-secret.yaml

5. Deploy Services
   kubectl apply -f services/

6. Deploy Core Deployments
   kubectl apply -f deployments/

Core deployments bao gồm:

Zookeeper, Kafka

HDFS Namenode & Datanode

Spark Master & Worker

Elasticsearch & Kibana

Airflow DB, Webserver, Scheduler

7. Deploy Jobs / Batch Spark Jobs
   kubectl apply -f jobs/

Các jobs bao gồm:

analyst_ohlcv

daily_ohlcv

mlib_evaluate

kafka_to_hdfs_ohlcv

kafka_to_hdfs_market

ohlcv_speed

speed_crawler

Jobs sẽ chạy 1 lần và kết thúc. Nếu muốn chạy lại, xóa job cũ:

kubectl delete job <job-name> -n bigdata
kubectl apply -f jobs/<job-yaml>

8. Kiểm tra trạng thái

# Kiểm tra pods

kubectl get pods -n bigdata

# Kiểm tra services

kubectl get svc -n bigdata

# Xem logs của pod

kubectl logs <pod-name> -n bigdata

9. Truy cập Web UI

Airflow Webserver: http://<minikube-ip>:8080

Spark Master UI: http://<minikube-ip>:8080

Elasticsearch: http://<minikube-ip>:9200

Kibana: http://<minikube-ip>:5601

Lấy Minikube IP:

minikube ip

10. Ghi chú

Tất cả các job Spark lấy config từ ConfigMap/Secret. Nếu cần chỉnh HDFS path, Kafka topic, hoặc ES index, chỉnh trong configmap/bigdata-config.yaml.

Sử dụng kubectl describe pod <pod> để debug nếu pod không chạy.

Các volume hostPath sẽ mount dữ liệu từ máy local, đảm bảo thư mục tồn tại:

./data/hdfs/namenode
./data/hdfs/datanode
./data/elasticsearch
./airflow/dags
./airflow/logs
