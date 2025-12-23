# Kubernetes Deployment - Triển khai hệ thống BigData trên K8s

Hướng dẫn triển khai toàn bộ hệ thống thu thập và phân tích dữ liệu chứng khoán lên Kubernetes cluster.

---

## 📋 Giới thiệu

Thư mục này chứa tất cả manifest files cần thiết để deploy hệ thống Lambda Architecture (Batch Layer + Speed Layer) lên Kubernetes:

- **Infrastructure Layer**: Kafka, Zookeeper, HDFS (NameNode, DataNode), Elasticsearch, Spark
- **Batch Layer**: Crawler batch, Kafka-to-HDFS jobs, Daily OHLCV, Analyst, MLlib
- **Speed Layer**: Speed crawler, OHLCV speed processor
- **Orchestration**: Airflow (scheduler, database)

---

## 🏗️ Cấu trúc thư mục

```
k8s-deployment/
├── namespace.yaml              # Tạo namespace "bigdata"
│
├── configmap/                  # Cấu hình tập trung
│   ├── bigdata-config.yaml    # Config cho HDFS, Kafka, Elasticsearch, Spark
│   └── kafka-config.yaml      # Config riêng cho Kafka
│
├── secrets/                    # Thông tin bảo mật
│   └── airflow-secret.yaml    # Credentials cho Airflow DB
│
├── deployments/                # Các deployment chạy liên tục
│   ├── zookeeper-deployment.yaml
│   ├── kafka-deployment.yaml
│   ├── namenode-deployment.yaml
│   ├── datanode-deployment.yaml
│   ├── elasticsearch-deployment.yaml
│   ├── spark-master-deployment.yaml
│   ├── spark-worker-deployment.yaml
│   ├── airflow-db-deployment.yaml
│   ├── crawler-deployment.yaml
│   ├── speed-crawler-deployment.yaml
│   ├── ohlcv-speed-deployment.yaml
│   ├── kafka-to-hdfs-market-deployment.yaml
│   ├── kafka-to-hdfs-ohlcv-deployment.yaml
│   ├── daily-ohlcv-deployment.yaml
│   ├── analyst-ohlcv-deployment.yaml
│   └── mlib-evaluate-deployment.yaml
│
├── services/                   # Expose services trong cluster
│   ├── zookeeper-service.yaml
│   ├── kafka-service.yaml
│   ├── namenode-service.yaml
│   ├── datanode-service.yaml
│   ├── elasticsearch-service.yaml
│   ├── spark-master-service.yaml
│   └── airflow-db-service.yaml
│
└── jobs/                       # Kubernetes CronJob hoặc Job (chạy 1 lần/theo lịch)
    ├── crawler-job.yaml
    ├── kafka-to-hdfs-market-job.yaml
    ├── kafka-to-hdfs-ohlcv-job.yaml
    ├── daily-ohlcv-job.yaml
    ├── ohlcv-analysis-job.yaml
    ├── ohlch-speed-job.yaml
    ├── mlib-evaluate-job.yaml
    └── speed-crawler-job.yaml
```

---

## 📦 Các thành phần chính

### 1. Infrastructure Components

#### **Zookeeper** (`zookeeper-deployment.yaml`)
- Quản lý metadata cho Kafka cluster
- Port: `2181`
- Resource: 256Mi RAM, 0.3 CPU

#### **Kafka** (`kafka-deployment.yaml`)
- Message broker cho streaming data
- Port: `9092`
- Topics: `stock.ohlcv.raw`, `stock.market.raw`, `stock.market.speed.raw`
- Resource: 768Mi RAM, 0.8 CPU

#### **HDFS NameNode** (`namenode-deployment.yaml`)
- Quản lý metadata của HDFS
- Web UI: `9870`
- HDFS URI: `hdfs://namenode:8020`
- Resource: 1Gi RAM, 0.7 CPU

#### **HDFS DataNode** (`datanode-deployment.yaml`)
- Lưu trữ dữ liệu thực tế
- Resource: 1.5Gi RAM, 1.0 CPU

#### **Elasticsearch** (`elasticsearch-deployment.yaml`)
- Lưu trữ và truy vấn dữ liệu đã xử lý
- Port: `9200`
- Indices: `ohlcv_daily_v2`, `ohlcv_analysis`, `market_data_v1`, `stock_intraday`

#### **Spark** (`spark-master-deployment.yaml`, `spark-worker-deployment.yaml`)
- Spark Master: Điều phối các Spark jobs
  - Web UI: `8080`, Submit: `7077`
- Spark Worker: Thực thi các tasks
  - Resource: 2Gi RAM, 1.5 CPU

---

### 2. Batch Layer Components

#### **Crawler Batch** (`crawler-deployment.yaml`)
- Thu thập dữ liệu OHLCV và Market Index lịch sử
- Gửi vào Kafka topics: `stock.ohlcv.raw`, `stock.market.raw`
- Chạy theo schedule hoặc trigger thủ công

#### **Kafka to HDFS - OHLCV** (`kafka-to-hdfs-ohlcv-deployment.yaml`)
- Đọc từ Kafka topic `stock.ohlcv.raw`
- Ghi vào HDFS: `hdfs://namenode:8020/data/ohlcv`
- Format: Parquet, partitioned by `symbol`, `interval`, `trade_date`

#### **Kafka to HDFS - Market** (`kafka-to-hdfs-market-deployment.yaml`)
- Đọc từ Kafka topic `stock.market.raw`
- Ghi vào HDFS: `hdfs://namenode:8020/data/market`
- Format: Parquet, partitioned by `index_code`, `trade_date`

#### **Daily OHLCV** (`daily-ohlcv-deployment.yaml`)
- Xử lý dữ liệu OHLCV hàng ngày từ HDFS
- Ghi vào Elasticsearch index: `ohlcv_daily_v2`
- Chạy với Spark Submit

#### **Analyst OHLCV** (`analyst-ohlcv-deployment.yaml`)
- Tính toán chỉ số kỹ thuật: SMA, EMA, RSI, MACD, Bollinger Bands
- Xử lý incremental (chỉ tính toán dữ liệu mới)
- Ghi vào Elasticsearch index: `ohlcv_analysis`

#### **MLlib Evaluate** (`mlib-evaluate-deployment.yaml`)
- Huấn luyện mô hình dự đoán giá cổ phiếu
- Models: Linear Regression, Random Forest
- Đánh giá: RMSE, R2 Score

---

### 3. Speed Layer Components

#### **Speed Crawler** (`speed-crawler-deployment.yaml`)
- Thu thập dữ liệu real-time (tick-by-tick)
- Gửi vào Kafka topic: `stock.market.speed.raw`

#### **OHLCV Speed** (`ohlcv-speed-deployment.yaml`)
- Tổng hợp dữ liệu real-time thành nến OHLCV
- Ghi vào Elasticsearch index: `stock_intraday`

---

### 4. Orchestration - Airflow

#### **Airflow DB** (`airflow-db-deployment.yaml`)
- PostgreSQL database cho Airflow metadata
- Port: `5432`

---

## 🚀 Hướng dẫn triển khai

### Yêu cầu:
- Kubernetes cluster (v1.20+)
- kubectl CLI configured
- Docker images đã build sẵn cho các services

### Bước 1: Tạo namespace

```bash
kubectl apply -f namespace.yaml
```

### Bước 2: Tạo ConfigMap và Secret

```bash
# ConfigMaps
kubectl apply -f configmap/bigdata-config.yaml
kubectl apply -f configmap/kafka-config.yaml

# Secrets
kubectl apply -f secrets/airflow-secret.yaml
```

### Bước 3: Deploy Infrastructure (theo thứ tự)

```bash
# 1. Zookeeper (cần cho Kafka)
kubectl apply -f deployments/zookeeper-deployment.yaml
kubectl apply -f services/zookeeper-service.yaml

# Chờ Zookeeper ready
kubectl wait --for=condition=ready pod -l app=zookeeper -n bigdata --timeout=120s

# 2. Kafka
kubectl apply -f deployments/kafka-deployment.yaml
kubectl apply -f services/kafka-service.yaml

# 3. HDFS
kubectl apply -f deployments/namenode-deployment.yaml
kubectl apply -f services/namenode-service.yaml
kubectl apply -f deployments/datanode-deployment.yaml
kubectl apply -f services/datanode-service.yaml

# 4. Elasticsearch
kubectl apply -f deployments/elasticsearch-deployment.yaml
kubectl apply -f services/elasticsearch-service.yaml

# 5. Spark
kubectl apply -f deployments/spark-master-deployment.yaml
kubectl apply -f services/spark-master-service.yaml
kubectl apply -f deployments/spark-worker-deployment.yaml
```

### Bước 4: Deploy Batch Layer

```bash
# Crawler
kubectl apply -f deployments/crawler-deployment.yaml

# Kafka to HDFS
kubectl apply -f deployments/kafka-to-hdfs-ohlcv-deployment.yaml
kubectl apply -f deployments/kafka-to-hdfs-market-deployment.yaml

# Processing jobs
kubectl apply -f deployments/daily-ohlcv-deployment.yaml
kubectl apply -f deployments/analyst-ohlcv-deployment.yaml
kubectl apply -f deployments/mlib-evaluate-deployment.yaml
```

### Bước 5: Deploy Speed Layer

```bash
kubectl apply -f deployments/speed-crawler-deployment.yaml
kubectl apply -f deployments/ohlcv-speed-deployment.yaml
```

### Bước 6: Deploy Airflow (optional)

```bash
kubectl apply -f deployments/airflow-db-deployment.yaml
kubectl apply -f services/airflow-db-service.yaml
```

### Bước 7: Deploy Jobs (CronJob - chạy theo lịch)

```bash
kubectl apply -f jobs/crawler-job.yaml
kubectl apply -f jobs/kafka-to-hdfs-ohlcv-job.yaml
kubectl apply -f jobs/daily-ohlcv-job.yaml
kubectl apply -f jobs/ohlcv-analysis-job.yaml
```

---

## 📊 Kiểm tra trạng thái

### Xem tất cả pods:
```bash
kubectl get pods -n bigdata
```

### Xem logs của một pod:
```bash
kubectl logs -f <pod-name> -n bigdata
```

### Xem services:
```bash
kubectl get svc -n bigdata
```

### Describe pod (debug):
```bash
kubectl describe pod <pod-name> -n bigdata
```

### Truy cập vào container:
```bash
kubectl exec -it <pod-name> -n bigdata -- /bin/bash
```

---

## 🔧 Cấu hình quan trọng (ConfigMap)

File: `configmap/bigdata-config.yaml`

```yaml
HDFS_PATH: "hdfs://namenode:8020/data/ohlcv"
HDFS_PATH_MARKET: "hdfs://namenode:8020/data/market"
ES_HOST: "http://elasticsearch:9200"
ES_INDEX_BATCH_OHLCV_DAILY: "ohlcv_daily_v2"
ES_INDEX_BATCH_OHLCV_ANAYLYST: "ohlcv_analysis"
ES_INDEX_BATCH_MARKET: "market_data_v1"
ES_INDEX_SPEED_STOCK: "stock_intraday"
SPARK_MASTER: "spark://spark-master:7077"
KAFKA_BOOTSTRAP: "kafka:9092"
KAFKA_TOPIC_BATCH_OHLCV: "stock.ohlcv.raw"
KAFKA_TOPIC_BATCH_MARKET: "stock.market.raw"
KAFKA_TOPIC_SPEED_STOCK: "stock.market.speed.raw"
SYMBOLS: "FPT,VNM,VCB"
DATA_SOURCE: "VCI"
```

### Cập nhật ConfigMap:
```bash
# Chỉnh sửa file
vim configmap/bigdata-config.yaml

# Apply changes
kubectl apply -f configmap/bigdata-config.yaml

# Restart pods để áp dụng config mới
kubectl rollout restart deployment <deployment-name> -n bigdata
```

---

## 🎯 Workflows phổ biến

### 1. Chạy Batch Processing Pipeline hoàn chỉnh:

```bash
# Step 1: Crawl dữ liệu → Kafka
kubectl create job --from=cronjob/crawler-job manual-crawler-$(date +%s) -n bigdata

# Step 2: Kafka → HDFS
kubectl create job --from=cronjob/kafka-to-hdfs-ohlcv-job manual-k2h-$(date +%s) -n bigdata

# Step 3: Xử lý Daily + Analyst
kubectl create job --from=cronjob/daily-ohlcv-job manual-daily-$(date +%s) -n bigdata
kubectl create job --from=cronjob/ohlcv-analysis-job manual-analyst-$(date +%s) -n bigdata
```

### 2. Kiểm tra Kafka topics:

```bash
# Exec vào Kafka pod
kubectl exec -it <kafka-pod-name> -n bigdata -- /bin/bash

# List topics
kafka-topics --list --bootstrap-server localhost:9092

# Đọc messages từ topic
kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic stock.ohlcv.raw --from-beginning --max-messages 10
```

### 3. Kiểm tra HDFS:

```bash
# Exec vào NameNode pod
kubectl exec -it <namenode-pod-name> -n bigdata -- /bin/bash

# List files trong HDFS
hdfs dfs -ls /data/ohlcv
hdfs dfs -ls /data/market

# Xem dung lượng
hdfs dfs -du -h /data
```

### 4. Query Elasticsearch:

```bash
# Port-forward Elasticsearch
kubectl port-forward svc/elasticsearch 9200:9200 -n bigdata

# Từ máy local
curl http://localhost:9200/_cat/indices?v
curl http://localhost:9200/ohlcv_daily_v2/_count
curl http://localhost:9200/ohlcv_daily_v2/_search?size=5
```

### 5. Truy cập Spark UI:

```bash
# Port-forward Spark Master UI
kubectl port-forward svc/spark-master 8080:8080 -n bigdata

# Mở browser: http://localhost:8080
```

---

## 🐳 Build Docker Images

Trước khi deploy, cần build các Docker images:

```bash
# Crawler
cd ../batch/crawler_batch
docker build -t crawler:latest .

# Daily OHLCV
cd ../batch/jobs/ohlcv/daily
docker build -t daily_ohlcv:latest .

# Analyst OHLCV
cd ../batch/jobs/ohlcv/analyst
docker build -t analyst_ohlcv:latest .

# MLlib
cd ../batch/jobs/ohlcv/mlib_evaluate
docker build -t mlib_evaluate:latest .

# Speed Crawler
cd ../speed/crawler_speed
docker build -t speed-crawler:latest .

# OHLCV Speed
cd ../speed/ohlcv
docker build -t ohlcv-speed:latest .
```

**Lưu ý:** Nếu dùng private registry, cần push images và update `image:` trong deployment files.

---

## 🔐 Quản lý Secrets

File: `secrets/airflow-secret.yaml`

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: airflow-secret
  namespace: bigdata
type: Opaque
data:
  postgres-password: <base64-encoded-password>
```

Tạo secret mới:
```bash
kubectl create secret generic my-secret \
  --from-literal=username=admin \
  --from-literal=password=secret123 \
  -n bigdata
```

---

## 📈 Scaling

### Scale Spark Workers:
```bash
kubectl scale deployment spark-worker --replicas=3 -n bigdata
```

### Scale Datanode:
```bash
kubectl scale deployment datanode --replicas=2 -n bigdata
```

### Horizontal Pod Autoscaler (HPA):
```bash
kubectl autoscale deployment spark-worker \
  --cpu-percent=70 --min=2 --max=5 -n bigdata
```

---

## 🐛 Troubleshooting

### Pod không start được:
```bash
# Xem events
kubectl describe pod <pod-name> -n bigdata

# Xem logs
kubectl logs <pod-name> -n bigdata

# Xem logs của container init (nếu có)
kubectl logs <pod-name> -c <init-container-name> -n bigdata
```

### ImagePullBackOff error:
```bash
# Kiểm tra image name
kubectl describe pod <pod-name> -n bigdata | grep Image

# Kiểm tra imagePullSecrets (nếu dùng private registry)
kubectl get secret -n bigdata
```

### CrashLoopBackOff:
```bash
# Xem logs trước khi crash
kubectl logs <pod-name> --previous -n bigdata

# Kiểm tra liveness/readiness probe
kubectl describe pod <pod-name> -n bigdata | grep -A 5 Liveness
```

### Service không kết nối được:
```bash
# Kiểm tra endpoints
kubectl get endpoints <service-name> -n bigdata

# Test connectivity từ pod khác
kubectl run -it --rm debug --image=busybox --restart=Never -n bigdata -- sh
wget -O- http://kafka:9092
```

---

## 🧹 Dọn dẹp

### Xóa toàn bộ namespace (cẩn thận!):
```bash
kubectl delete namespace bigdata
```

### Xóa từng component:
```bash
kubectl delete -f deployments/ -n bigdata
kubectl delete -f jobs/ -n bigdata
kubectl delete -f services/ -n bigdata
kubectl delete -f configmap/ -n bigdata
kubectl delete -f secrets/ -n bigdata
```

---

## 📚 Tham khảo

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Kubernetes Patterns](https://kubernetes.io/docs/concepts/cluster-administration/manage-deployment/)
- [Spark on Kubernetes](https://spark.apache.org/docs/latest/running-on-kubernetes.html)