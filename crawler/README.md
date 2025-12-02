# 📦 Crawler – Thu thập dữ liệu chứng khoán Việt Nam

Crawler thu thập dữ liệu chứng khoán Việt Nam, bao gồm **OHLCV**, **Fundamental**, và **Market**, với khả năng chạy độc lập hoặc trong pipeline tổng thể.

---

## 📋 Giới thiệu

Crawler sử dụng thư viện **vnstock3** để thu thập dữ liệu từ các sàn HOSE, HNX, UPCOM:

- **OHLCV**: Dữ liệu giá lịch sử (Open, High, Low, Close, Volume)  
- **Fundamental**: Báo cáo tài chính, chỉ số tài chính, thông tin công ty  
- **Market**: Chỉ số thị trường (VN-Index, HNX-Index), danh sách cổ phiếu  

Crawler có thể chạy từng module riêng hoặc chạy toàn bộ pipeline.

---

## 🏗️ Cấu trúc thư mục (hiển thị folder, bỏ `data` và `.py`)

crawler/
├── Dockerfile
├── README.md
├── requirements.txt
└── src/ # Source code crawler
└── pycache/


---

## 🚀 Hướng dẫn sử dụng

### 1️⃣ Clone repository

```bash
git clone <repository-url>
cd crawler

2️⃣ Tạo virtual environment (khuyến nghị)

python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# hoặc
.venv\Scripts\activate     # Windows

3️⃣ Cài đặt thư viện Python

pip install -r requirements.txt

🐳 Chạy crawler với Docker
1️⃣ Build Docker image

docker build -t bigdata/crawler:latest .

2️⃣ Chạy container với volume mount

docker run -it \
  -v /home/anh/crawler_data:/app/data \
  -v /home/anh/crawler_logs:/app/logs \
  bigdata/crawler:latest python3 src/pipeline.py

    /app/data → mount ra host folder /home/anh/crawler_data

    /app/logs → mount ra host folder /home/anh/crawler_logs

    Chỉ mount các folder cần thiết để không ghi đè code trong container.

3️⃣ Debug interactive container

docker run -it \
  -v ../crawler:/app/data \
  -v ../crawler_logs:/app/logs \
  bigdata/crawler:latest bash

    Trong container: chạy thử pipeline hoặc các module riêng:

python3 src/pipeline.py
