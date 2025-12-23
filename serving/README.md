# Serving Layer - Lambda Architecture

RESTful API serving layer cho hệ thống Lambda Architecture xử lý dữ liệu chứng khoán.

## 🏗️ Architecture Overview

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│   FastAPI Server    │
│  (Serving Layer)    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Lambda Merger      │ ◄──────── Redis Cache
└──────┬──────────────┘
       │
       ├──────────────┐
       ▼              ▼
┌─────────────┐  ┌──────────────┐
│ Batch Layer │  │ Speed Layer  │
│(Elasticsearch)  │   (Kafka)    │
└─────────────┘  └──────────────┘
```

## 🚀 Features

### 1. **OHLCV Data API**
- Latest prices với cache 60s
- Historical data với pagination
- Multi-symbol batch queries
- Price statistics

### 2. **Technical Indicators API**
- Moving Averages (MA7, MA30)
- RSI (Relative Strength Index)
- Bollinger Bands
- VWAP (Volume Weighted Average Price)
- Returns (Daily & Cumulative)

### 3. **ML Predictions API** (Mock - sẵn sàng tích hợp)
- Linear Regression predictions
- Random Forest predictions
- Model accuracy metrics
- Prediction history

### 4. **Lambda Pattern Implementation**
- Merge batch views (Elasticsearch) + speed views (Kafka)
- Intelligent caching strategy
- Freshness checking

## 📦 Installation

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Elasticsearch running (from batch layer)
- Redis (included in compose)

### Setup

1. **Clone và navigate:**
```bash
cd serve/
```

2. **Create .env file:**
```bash
cp .env.example .env
# Edit .env với config phù hợp
```

3. **Build và run với Docker Compose:**
```bash
docker-compose up -d
```

4. **Hoặc run local (development):**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run server
python main.py
```

## 🔌 API Endpoints

### Base URL: `http://localhost:8000`

### Health Check
```bash
GET /api/v1/health
GET /api/v1/health/ping
GET /api/v1/health/detailed
```

### OHLCV Data
```bash
# Latest price
GET /api/v1/ohlcv/latest/{symbol}
GET /api/v1/ohlcv/latest?symbols=FPT,VNM,VCB

# Historical data
GET /api/v1/ohlcv/historical/{symbol}
    ?start_date=2024-01-01
    &end_date=2024-12-31
    &page=1
    &page_size=50

# Statistics
GET /api/v1/ohlcv/statistics/{symbol}?days=30

# Data freshness
GET /api/v1/ohlcv/freshness/{symbol}
```

### Technical Indicators
```bash
# All indicators
GET /api/v1/indicators/{symbol}
    ?start_date=2024-01-01
    &limit=30

# Latest indicators
GET /api/v1/indicators/{symbol}/latest

# Specific indicators
GET /api/v1/indicators/{symbol}/rsi?days=30
GET /api/v1/indicators/{symbol}/moving_averages?days=60
GET /api/v1/indicators/{symbol}/bollinger_bands?days=30
```

### ML Predictions
```bash
# Get predictions
GET /api/v1/predictions/{symbol}

# Model accuracy
GET /api/v1/predictions/{symbol}/accuracy

# All models status
GET /api/v1/predictions/models/status
```

## 📊 Example Usage

### cURL Examples

```bash
# Get latest price for FPT
curl http://localhost:8000/api/v1/ohlcv/latest/FPT

# Get technical indicators
curl http://localhost:8000/api/v1/indicators/FPT/latest

# Get RSI data
curl http://localhost:8000/api/v1/indicators/FPT/rsi?days=14

# Get predictions
curl http://localhost:8000/api/v1/predictions/FPT
```

### Python Example

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Get latest price
response = requests.get(f"{BASE_URL}/ohlcv/latest/FPT")
data = response.json()
print(f"FPT latest close: {data['latest_data']['close']}")

# Get indicators
response = requests.get(f"{BASE_URL}/indicators/FPT/latest")
indicators = response.json()
print(f"RSI: {indicators['rsi14']}")
print(f"MA30: {indicators['ma30']}")

# Get historical data
response = requests.get(
    f"{BASE_URL}/ohlcv/historical/FPT",
    params={
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "page_size": 100
    }
)
history = response.json()
print(f"Total records: {history['total_records']}")
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | false | Debug mode |
| `ES_HOST` | http://elasticsearch:9200 | Elasticsearch host |
| `REDIS_HOST` | redis | Redis host |
| `REDIS_PORT` | 6379 | Redis port |
| `CACHE_TTL_LATEST_PRICE` | 60 | Latest price cache TTL (seconds) |
| `CACHE_TTL_INDICATORS` | 300 | Indicators cache TTL |
| `ENABLE_SPEED_LAYER` | false | Enable Kafka speed layer |

### Cache Strategy

- **Latest Price**: 60s TTL (frequent updates expected)
- **Historical Data**: 1 hour TTL (stable historical data)
- **Indicators**: 5 minutes TTL (computed periodically)
- **Predictions**: 10 minutes TTL (model outputs)

## 🧪 Testing

### Interactive API Docs
Swagger UI: `http://localhost:8000/docs`
ReDoc: `http://localhost:8000/redoc`

### Health Checks
```bash
# Basic ping
curl http://localhost:8000/api/v1/health/ping

# Detailed health
curl http://localhost:8000/api/v1/health/detailed
```

### Cache Management
```bash
# Clear all cache
curl -X POST http://localhost:8000/api/v1/health/cache/clear

# Clear cache for specific symbol
curl -X POST http://localhost:8000/api/v1/health/cache/clear/FPT
```

## 🔄 Speed Layer Integration

### Khi Speed Layer sẵn sàng:

1. **Enable trong config:**
```bash
ENABLE_SPEED_LAYER=true
KAFKA_BOOTSTRAP=kafka:9092
KAFKA_TOPIC_SPEED_OHLCV=stock.ohlcv.speed
```

2. **Uncomment code trong `kafka_service.py`:**
- Line ~30: Initialize KafkaConsumer
- Line ~50: Consumer loop
- Line ~70: Message processing

3. **Restart service:**
```bash
docker-compose restart serving-api
```

4. **Verify integration:**
```bash
curl http://localhost:8000/api/v1/ohlcv/freshness/FPT
```

### Expected Speed Layer Message Format
```json
{
  "symbol": "FPT",
  "trade_date": "2024-12-21",
  "interval": "1D",
  "event_time": "2024-12-21T14:30:00Z",
  "data": {
    "open": 125000.0,
    "high": 127500.0,
    "low": 124000.0,
    "close": 126500.0,
    "volume": 1500000
  }
}
```

## 📈 Performance Optimization

### Current Optimizations:
- Redis caching với TTL thông minh
- Elasticsearch query optimization
- Connection pooling
- Async I/O operations

### Monitoring:
```bash
# Cache statistics
curl http://localhost:8000/api/v1/health/detailed

# Response includes:
# - Cache hit rate
# - Total keys
# - Hits/misses
```

## 🚀 Production Deployment

### Kubernetes Deployment
Xem file `k8s/serve-deployment.yaml` (sẽ tạo sau)

### Docker Production Build
```bash
# Build image
docker build -t serving-api:v1.0.0 .

# Run production
docker run -d \
  --name serving-api \
  --network bigdata-net \
  -p 8000:8000 \
  -e DEBUG=false \
  -e ES_HOST=http://elasticsearch:9200 \
  -e REDIS_HOST=redis \
  serving-api:v1.0.0
```

### Scaling
```bash
# Scale horizontally với load balancer
docker-compose up -d --scale serving-api=3
```

## 📝 Development Notes

### Mock Data
- **Predictions API**: Hiện tại trả về mock data
- **Speed Layer**: Disabled by default, có mock implementation

### TODO / Future Enhancements
- [ ] Implement real predictions storage
- [ ] Add authentication/authorization
- [ ] Add rate limiting
- [ ] Implement WebSocket for real-time updates
- [ ] Add metrics export (Prometheus)
- [ ] Add request tracing
- [ ] Implement GraphQL endpoint
- [ ] Add data validation middleware

## 🐛 Troubleshooting

### Cannot connect to Elasticsearch
```bash
# Check ES is running
curl http://localhost:9200

# Check network
docker network inspect bigdata-net
```

### Redis connection failed
```bash
# Test Redis
redis-cli -h localhost -p 6379 ping

# Check logs
docker logs redis
```

### No data returned
```bash
# Verify batch jobs have run
curl http://localhost:9200/ohlcv_daily_v2/_search

# Check if crawler + batch jobs completed
```

## 📚 API Documentation

Full API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## 👥 Contributing

Khi thêm endpoint mới:
1. Tạo route trong `api/routes/`
2. Add service logic trong `services/`
3. Update schema trong `models/schemas.py`
4. Add tests
5. Update README

## 📄 License

[Your License Here]