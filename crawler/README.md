# Dự án Thu thập và Phân tích Dữ liệu Chứng khoán Việt Nam

Pipeline:   
![Kien truc su dung](./pipe_line.png)

## 📋 Giới thiệu
Dự án sử dụng thư viện **vnstock3** để thu thập dữ liệu chứng khoán từ thị trường Việt Nam, bao gồm:
- 📊 **OHLCV**: Dữ liệu giá lịch sử (Open, High, Low, Close, Volume)
- 📈 **Fundamental**: Báo cáo tài chính, chỉ số tài chính, thông tin công ty
- 📉 **Market**: Chỉ số thị trường (VN-Index, HNX-Index), danh sách cổ phiếu

## 🏗️ Cấu trúc thư mục
```
BTL_BigData/
├── config.py                          # File cấu hình (danh sách mã, tham số)
├── pipeline.py                        # Pipeline chính điều phối toàn bộ
├── historical_ohlcv_crawler.py        # Crawler dữ liệu OHLCV
├── fundamental_analyst_crawler.py     # Crawler dữ liệu fundamental
├── market_crawler.py                  # Crawler dữ liệu thị trường
├── save.py                            # Utilities lưu trữ dữ liệu
├── requirements.txt                   # Dependencies
├── data/                              # Thư mục chứa dữ liệu
│   ├── ohlcv/                        # Dữ liệu giá
│   ├── fundamental/                   # Dữ liệu tài chính
│   └── market/                        # Dữ liệu thị trường
└── logs/                              # Log files
```

## 🚀 Cài đặt

### 1. Clone repository
```bash
git clone <repository-url>
cd BTL_BigData
```

### 2. Tạo virtual environment (khuyến nghị)
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# hoặc
.venv\Scripts\activate     # Windows
```

### 3. Cài đặt dependencies
```bash
pip install -r requirements.txt
```
## 📝 Chi tiết các module

### 1. `historical_ohlcv_crawler.py`
Thu thập dữ liệu giá lịch sử:
- Daily (1D), Weekly (1W), Monthly (1M)
- Intraday (dữ liệu trong ngày)

### 2. `fundamental_analyst_crawler.py`
Thu thập dữ liệu phân tích cơ bản:
- Thông tin công ty
- Báo cáo tài chính (BCĐKT, KQKD, LCTT)
- Chỉ số tài chính
- Lịch sử cổ tức

### 3. `market_crawler.py`
Thu thập dữ liệu thị trường:
- Chỉ số VN-Index, HNX-Index
- Danh sách tất cả mã cổ phiếu theo sàn

### 4. `save.py`
Utilities để lưu trữ và quản lý file:

## ⚙️ Tùy chỉnh

### Thêm mã cổ phiếu mới
Chỉnh sửa `config.py`:
```python
SYMBOLS = [
    'FPT', 'VNM', 'VCB',  # Mã hiện có
    'MSN', 'MWG', 'POW',  # Thêm mã mới
]
```

### Thay đổi khoảng thời gian
```python
# Trong config.py
START_DATE_3Y = (datetime.now() - timedelta(days=365*3)).strftime('%Y-%m-%d')
```

### Tắt/bật các crawler
```python
# Trong config.py
class CrawlerConfig:
    OHLCV = {'enabled': True}
    FUNDAMENTAL = {'enabled': True}
    MARKET = {'enabled': False}  # Tắt crawler market
```

## 🔍 Kiểm tra dữ liệu đã thu thập

```bash
# Xem danh sách files
ls -lh data/ohlcv/
ls -lh data/fundamental/
ls -lh data/market/

# Hoặc sử dụng Python
python -c "from save import DataSaver; saver = DataSaver(); print(saver.get_file_info('ohlcv'))"
```

## 📊 Output mẫu

### OHLCV Data
```csv
time,open,high,low,close,volume
2024-01-02,85.5,86.2,85.0,86.0,2500000
2024-01-03,86.0,87.5,85.8,87.2,3100000
```

### Fundamental Data
```csv
ticker,yearReport,revenue,profit,asset,equity
FPT,2023,50000,8000,45000,25000
FPT,2022,45000,7000,42000,23000
```