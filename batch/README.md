# Batch Layer – Xử lý dữ liệu chứng khoán theo lô

Batch Layer chịu trách nhiệm thu thập, xử lý và phân tích dữ liệu chứng khoán lịch sử theo từng lô (batch), đảm bảo tính toàn vẹn và chính xác của dữ liệu.

---

## 📋 Giới thiệu

Batch Layer trong kiến trúc Lambda Architecture thực hiện các tác vụ:

- **Thu thập dữ liệu lịch sử**: Crawl dữ liệu OHLCV (Open, High, Low, Close, Volume) và Market Index từ các nguồn
- **Lưu trữ vào HDFS**: Đọc dữ liệu từ Kafka, xử lý bằng Spark và lưu vào HDFS theo định dạng Parquet
- **Phân tích và chỉ số kỹ thuật**: Tính toán các chỉ số như SMA, EMA, RSI, MACD cho phân tích kỹ thuật
- **Dự đoán giá**: Sử dụng Spark MLlib để huấn luyện mô hình dự đoán giá cổ phiếu
- **Đồng bộ vào Elasticsearch**: Đưa dữ liệu đã xử lý vào Elasticsearch để truy vấn nhanh

---

## 🏗️ Cấu trúc thư mục

```
batch/
├── crawler_batch/              # Module thu thập dữ liệu batch
│   ├── config.py              # Cấu hình crawler (symbols, date range, kafka)
│   ├── kafka_producer.py      # Gửi dữ liệu vào Kafka
│   ├── main.py                # Entry point chạy crawler
│   ├── Dockerfile
│   ├── requirements.txt
│   └── crawlers/
│       ├── ohlcv_crawler.py   # Crawl dữ liệu giá OHLCV
│       ├── market_crawler.py  # Crawl chỉ số thị trường (VN-Index, HNX-Index)
│       └── fundamental_crawler.py  # Crawl dữ liệu cơ bản
│
└── jobs/                       # Các job xử lý dữ liệu với Spark
    ├── market/
    │   └── kafka_to_hdfs_market/
    │       ├── kafka_to_hdfs_market.py  # Đọc Kafka → ghi HDFS (market data)
    │       ├── Dockerfile
    │       └── requirements.txt
    │
    └── ohlcv/
        ├── kafka_to_hdfs_ohlcv/
        │   ├── kafka_to_hdfs_ohlcv.py   # Đọc Kafka → ghi HDFS (OHLCV)
        │   ├── Dockerfile
        │   └── requirements.txt
        │
        ├── daily/
        │   ├── daily_ohlcv.py           # Xử lý OHLCV hàng ngày → Elasticsearch
        │   ├── Dockerfile
        │   └── requirements.txt
        │
        ├── analyst/
        │   ├── analyst_ohlcv.py         # Tính các chỉ số kỹ thuật (SMA, EMA, RSI, MACD)
        │   ├── Dockerfile
        │   └── requirements.txt
        │
        └── mlib_evaluate/
            ├── mlib_evaluate.py         # Huấn luyện mô hình dự đoán giá (Linear Regression, Random Forest)
            ├── Dockerfile
            └── requirements.txt
```

---

## ⚙️ Các thành phần chính

### 1. Crawler Batch (`crawler_batch/`)

**Chức năng:**
- Thu thập dữ liệu lịch sử OHLCV từ VCI/TCBS qua thư viện vnstock3
- Thu thập chỉ số thị trường (VNINDEX, HNX-INDEX)
- Gửi dữ liệu vào Kafka topics: `stock.ohlcv.raw`, `stock.market.raw`

**Cấu hình chính** (trong `config.py`):
```python
SYMBOLS = ["FPT", "VNM", "VCB"]  # Danh sách mã cổ phiếu
DATA_SOURCE = "VCI"               # Nguồn dữ liệu: VCI hoặc TCBS
START_DATE = "2024-01-01"         # Ngày bắt đầu crawl
END_DATE = "2024-12-31"           # Ngày kết thúc
KAFKA_BOOTSTRAP = "kafka:9092"    # Kafka server
TOPIC_OHLCV_RAW = "stock.ohlcv.raw"
TOPIC_MARKET_RAW = "stock.market.raw"
```

**Chạy crawler:**
```bash
cd crawler_batch
python main.py
```

---

### 2. Kafka to HDFS Jobs

#### a) `kafka_to_hdfs_ohlcv` - Lưu OHLCV vào HDFS
- Đọc dữ liệu từ Kafka topic `stock.ohlcv.raw`
- Parse JSON và chuyển thành DataFrame
- Lưu vào HDFS dạng Parquet, partition theo: `symbol`, `interval`, `trade_date`

**Chạy job:**
```bash
spark-submit \
  --master spark://spark-master:7077 \
  kafka_to_hdfs_ohlcv.py
```

#### b) `kafka_to_hdfs_market` - Lưu Market data vào HDFS
- Đọc dữ liệu từ Kafka topic `stock.market.raw`
- Lưu vào HDFS, partition theo: `index_code`, `trade_date`

**Chạy job:**
```bash
spark-submit \
  --master spark://spark-master:7077 \
  kafka_to_hdfs_market.py
```

---

### 3. Daily OHLCV Processing (`daily/`)

**Chức năng:**
- Đọc dữ liệu OHLCV từ HDFS
- Flatten dữ liệu và chuẩn hóa định dạng ngày
- Ghi vào Elasticsearch index `ohlcv_daily_v2` để truy vấn nhanh

**Chạy job:**
```bash
spark-submit \
  --master spark://spark-master:7077 \
  --packages org.elasticsearch:elasticsearch-spark-30_2.12:8.11.0 \
  daily_ohlcv.py
```

---

### 4. Analyst OHLCV (`analyst/`)

**Chức năng:**
- Tính toán các chỉ số kỹ thuật (Technical Indicators):
  - **SMA** (Simple Moving Average): Trung bình động giản đơn
  - **EMA** (Exponential Moving Average): Trung bình động mũ
  - **RSI** (Relative Strength Index): Chỉ số sức mạnh tương đối
  - **MACD** (Moving Average Convergence Divergence): Hội tụ phân kỳ trung bình động
  - **Bollinger Bands**: Dải Bollinger
- Xử lý incremental: chỉ tính toán dữ liệu mới từ lần chạy trước
- Lưu kết quả vào Elasticsearch index `ohlcv_analysis`

**Chạy job:**
```bash
spark-submit \
  --master spark://spark-master:7077 \
  --packages org.elasticsearch:elasticsearch-spark-30_2.12:8.11.0 \
  analyst_ohlcv.py
```

---

### 5. MLlib Evaluate (`mlib_evaluate/`)

**Chức năng:**
- Huấn luyện mô hình Machine Learning dự đoán giá cổ phiếu
- Sử dụng dữ liệu OHLCV từ HDFS
- Mô hình: Linear Regression và Random Forest Regressor
- Features: open, high, low, close, volume
- Label: giá đóng cửa ngày tiếp theo (close_next)
- Đánh giá mô hình: RMSE, R2 Score

**Chạy job:**
```bash
spark-submit \
  --master spark://spark-master:7077 \
  mlib_evaluate.py
```

---

## 🚀 Hướng dẫn sử dụng

### Yêu cầu hệ thống:
- Python 3.9+
- Apache Spark 3.x
- Kafka 2.8+
- Hadoop HDFS 3.x
- Elasticsearch 8.x

### Cài đặt dependencies:

```bash
# Crawler
cd crawler_batch
pip install -r requirements.txt

# Jobs (mỗi job có requirements.txt riêng)
cd jobs/ohlcv/daily
pip install -r requirements.txt
```

### Workflow hoàn chỉnh:

```bash
# Bước 1: Chạy crawler để thu thập dữ liệu → Kafka
cd crawler_batch
python main.py

# Bước 2: Chuyển dữ liệu từ Kafka → HDFS
spark-submit jobs/ohlcv/kafka_to_hdfs_ohlcv/kafka_to_hdfs_ohlcv.py
spark-submit jobs/market/kafka_to_hdfs_market/kafka_to_hdfs_market.py

# Bước 3: Xử lý dữ liệu hàng ngày → Elasticsearch
spark-submit --packages org.elasticsearch:elasticsearch-spark-30_2.12:8.11.0 \
  jobs/ohlcv/daily/daily_ohlcv.py

# Bước 4: Tính toán chỉ số kỹ thuật → Elasticsearch
spark-submit --packages org.elasticsearch:elasticsearch-spark-30_2.12:8.11.0 \
  jobs/ohlcv/analyst/analyst_ohlcv.py

# Bước 5: Huấn luyện mô hình ML dự đoán
spark-submit jobs/ohlcv/mlib_evaluate/mlib_evaluate.py
```

---

## 🐳 Chạy với Docker

Mỗi module có Dockerfile riêng:

```bash
# Build image crawler
cd crawler_batch
docker build -t crawler-batch:latest .

# Build image job
cd jobs/ohlcv/daily
docker build -t daily-ohlcv:latest .

# Chạy container
docker run --rm --network bigdata-net crawler-batch:latest
```

---

## 📊 Luồng dữ liệu (Data Flow)

```
┌─────────────┐
│  Crawler    │  Thu thập OHLCV, Market Index
│   Batch     │  
└──────┬──────┘
       │ JSON
       ▼
┌─────────────┐
│    Kafka    │  Topics: stock.ohlcv.raw, stock.market.raw
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Kafka→HDFS  │  Spark Batch Job: Parse & Write Parquet
│    Jobs     │  
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    HDFS     │  Lưu trữ dữ liệu dạng Parquet, partitioned
└──────┬──────┘
       │
       ├──────────────┐
       │              │
       ▼              ▼
┌────────────┐  ┌───────────┐
│   Daily    │  │  Analyst  │  Tính chỉ số kỹ thuật
│   OHLCV    │  │   OHLCV   │  (SMA, EMA, RSI, MACD)
└──────┬─────┘  └─────┬─────┘
       │              │
       ▼              ▼
┌──────────────────────┐
│   Elasticsearch      │  Index: ohlcv_daily_v2, ohlcv_analysis
└──────────────────────┘
       │
       ▼
┌──────────────────────┐
│ Dashboard/Kibana     │  Visualization & Query
└──────────────────────┘
```

---

## 🔧 Biến môi trường

Các biến môi trường quan trọng (có thể set qua ConfigMap trong K8s):

```bash
# Kafka
KAFKA_BOOTSTRAP=kafka:9092
KAFKA_TOPIC_BATCH_OHLCV=stock.ohlcv.raw
KAFKA_TOPIC_BATCH_MARKET=stock.market.raw

# HDFS
HDFS_PATH=hdfs://namenode:8020/data/ohlcv
HDFS_PATH_MARKET=hdfs://namenode:8020/data/market

# Elasticsearch
ES_HOST=http://elasticsearch:9200
ES_INDEX_BATCH_OHLCV_DAILY=ohlcv_daily_v2
ES_INDEX_BATCH_OHLCV_ANAYLYST=ohlcv_analysis

# Spark
SPARK_MASTER=spark://spark-master:7077

# Crawler Config
SYMBOLS=FPT,VNM,VCB
DATA_SOURCE=VCI
START_DATE=2024-01-01
END_DATE=2024-12-31
```

---

## 📝 Lưu ý

- Crawler chạy 1 lần/ngày hoặc theo schedule từ Airflow
- Jobs Kafka→HDFS nên chạy sau khi crawler hoàn thành
- Analyst job xử lý incremental để tránh tính toán lại toàn bộ
- MLlib job có thể chạy định kỳ (1 tuần/lần) để cập nhật mô hình

---

## 🐛 Troubleshooting

**Lỗi: Kafka connection refused**
```bash
# Kiểm tra Kafka đã chạy chưa
kubectl get pods -n bigdata | grep kafka
# hoặc
docker ps | grep kafka
```

**Lỗi: HDFS namenode not found**
```bash
# Kiểm tra HDFS namenode
hdfs dfsadmin -report
```

**Lỗi: Elasticsearch index not found**
```bash
# Tạo index mapping trước
curl -X PUT "http://elasticsearch:9200/ohlcv_daily_v2"
```

---

## 📚 Tham khảo

- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [Kafka Python Client](https://kafka-python.readthedocs.io/)
- [vnstock3 Documentation](https://vnstock.site/)
- [Elasticsearch Spark Integration](https://www.elastic.co/guide/en/elasticsearch/hadoop/current/spark.html)