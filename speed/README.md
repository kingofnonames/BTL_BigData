# Speed Layer: Real-time Data Pipeline

Tài liệu này hướng dẫn triển khai Speed Layer - thành phần chịu trách nhiệm thu thập và xử lý dữ liệu chứng khoán thời gian thực.
Module này hoạt động độc lập để đảm bảo độ trễ thấp và tính toàn vẹn dữ liệu.

# Luồng dữ liệu

Ingestion (Thu thập): src/producer_realtime.py gọi API chứng khoán (vnstock) và đẩy vào hàng đợi.
Buffering (Đệm): Apache Kafka lưu trữ tạm thời các bản tin để chịu tải.
Processing (Xử lý): src/speed_layer.py (Spark Streaming) đọc từ Kafka, làm sạch, ép kiểu và chuẩn hóa dữ liệu.
Sink (Đích đến): Ghi dữ liệu đã xử lý xuống kho lưu trữ (Elasticsearch) hoặc in ra màn hình (Console).

# Yêu cầu Hệ thống

OS: Linux (Ubuntu/WSL2).
Java JDK 11
Docker & Docker Compose
Python 3.8+

# Cài đặt & Cấu hình

## 1. Chuẩn bị Hạ tầng 

Speed Layer cần Kafka (để đệm tin) và Elasticsearch (để lưu kết quả). Tạo file docker-compose-speed.yml (hoặc dùng file chung):
```csv
version: '3'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.4.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000

  kafka:
    image: confluentinc/cp-kafka:7.4.0
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1

  # Sink Storage (Nơi chứa dữ liệu sau xử lý)
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.1
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
```

Khởi động hạ tầng:
```csv
docker-compose -f docker-compose-speed.yml up -d
```

## 2. Cài đặt thư viện Python
```csv
python3 -m venv .venv
source .venv/bin/activate
pip install pyspark==3.5.0 pandas numpy kafka-python vnstock3
```

# Hướng dẫn Vận hành (Execution)

Mở 2 Terminal riêng biệt để quan sát luồng dữ liệu.

Terminal 1: Khởi động Bộ xử lý (Spark Consumer)

Đây là "trái tim" của Speed Layer, chịu trách nhiệm đọc và xử lý luồng dữ liệu.
```csv
source .venv/bin/activate
python src/speed_layer.py
```

Dấu hiệu thành công: Terminal hiện log --- [PROCESSING]... và Batch: 0, Batch: 1... (Spark đang lắng nghe).

Terminal 2: Khởi động Nguồn dữ liệu (Producer)

Đây là script giả lập hoặc lấy dữ liệu thật để bơm vào hệ thống.
```csv
source .venv/bin/activate
python src/producer_realtime.py
```

Dấu hiệu thành công: Terminal liên tục in log [BUFFERED] FPT | 98.5...

# Kiểm tra Kết quả (Verification)

Cách 1: Kiểm tra Log Terminal 1 (Spark)
Nếu Spark đang chạy tốt, nó sẽ in ra tiến độ xử lý (Progress report) cho từng Batch.

Cách 2: Kiểm tra Kafka (Dữ liệu thô)
Xem dữ liệu có thực sự vào Kafka không:
```csv
docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic stock_realtime --from-beginning
```

Cách 3: Kiểm tra Elasticsearch (Dữ liệu đích)
Kiểm tra xem dữ liệu đã được lưu thành công chưa bằng lệnh curl:
```csv
# Đếm số lượng bản ghi đã xử lý
curl -X GET "localhost:9200/stock_realtime/_count?pretty"

# Xem 1 bản ghi mẫu
curl -X GET "localhost:9200/stock_realtime/_search?size=1&pretty"
```

# Troubleshooting

Lỗi Kafka Connection: Đảm bảo producer_realtime.py trỏ đúng localhost:9092.

Lỗi Spark Library: Đảm bảo máy đã có mạng internet để Spark tải gói spark-sql-kafka trong lần chạy đầu tiên.

Lỗi Checkpoint: Nếu gặp lỗi đường dẫn, xóa thư mục tạm: rm -rf /tmp/spark_checkpoint_speed.
