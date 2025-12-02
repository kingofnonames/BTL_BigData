# Serving Layer – Xử lý & Trực quan hóa dữ liệu chứng khoán
Serving Layer đảm nhận việc xử lý dữ liệu (Batch & Real-time) bằng Spark, lưu trữ tập trung tại Elasticsearch và trực quan hóa dữ liệu lên Dashboard Kibana.

# Giới thiệu
Module sử dụng bộ công nghệ ELK Stack kết hợp với Spark để phục vụ dữ liệu:

Batch Processing: Đọc dữ liệu lịch sử (OHLCV, Fundamental) từ file, chuẩn hóa và Index vào Elasticsearch.

Speed Processing (Real-time): Đọc luồng dữ liệu giao dịch từ Kafka, xử lý qua Spark Streaming và cập nhật bảng điện tử tức thời.

Visualization: Cung cấp Dashboard Kibana để theo dõi biến động giá, khối lượng và các chỉ số phân tích.

Module có thể chạy chế độ nạp dữ liệu lịch sử (Batch) hoặc lắng nghe thời gian thực (Streaming).

# Cấu trúc thư mục
Plaintext

serving/
├── config/              # Cấu hình kết nối ES, Kafka
├── Dockerfile           # Docker image cho Spark App
├── docker-compose.yml   # Hạ tầng ES, Kibana, Kafka
├── README.md
├── requirements.txt
└── src/                 # Source code Spark jobs
    └── __pycache__/
# Hướng dẫn sử dụng
1. Clone repository
Bash

git clone <repository-url>
cd serving
2. Tạo virtual environment (khuyến nghị)
Bash

python -m venv .venv
source .venv/bin/activate  # Linux/Mac

.venv\Scripts\activate     # Windows
3️. Cài đặt thư viện Python
Bash

pip install -r requirements.txt
(Yêu cầu: Đã cài đặt Java JDK 11 để chạy Spark local)

# Chạy Serving Layer với Docker
1️. Khởi động hạ tầng (Infrastructure)
Trước khi chạy code xử lý, cần bật Elasticsearch, Kibana và Kafka:

Bash

docker-compose up -d
Elasticsearch: http://localhost:9200

Kibana: http://localhost:5601

2️. Build Docker image (Spark App)
Bash

docker build -t bigdata/serving:latest .
3️. Chạy container xử lý dữ liệu
Chạy container để thực thi Spark Job, cần mount volume dữ liệu và kết nối cùng network với hạ tầng trên.

Chạy Batch Layer (Nạp dữ liệu lịch sử):

Bash

docker run -it --network serving_stock-net \
  -v /home/user/project/data:/app/data \
  -v /home/user/project/logs:/app/logs \
  bigdata/serving:latest python3 src/serving_layer.py
Chạy Speed Layer (Xử lý Real-time):

Bash

docker run -it --network serving_stock-net \
  -v /home/user/project/logs:/app/logs \
  bigdata/serving:latest python3 src/speed_layer.py
/app/data → mount ra host folder chứa dữ liệu CSV đã crawl (để Batch layer đọc).

--network serving_stock-net → Bắt buộc để Spark trong container nhìn thấy Elasticsearch và Kafka.

4️. Debug interactive container
Nếu muốn vào trong container để kiểm tra môi trường hoặc chạy thử lệnh thủ công:

Bash

docker run -it --network serving_stock-net \
  -v ../data:/app/data \
  bigdata/serving:latest bash
Trong container:

Bash

# Kiểm tra kết nối tới Elastic
curl http://elasticsearch:9200

# Chạy job thủ công
python3 src/serving_layer.py


