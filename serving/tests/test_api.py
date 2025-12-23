#!/usr/bin/env python3
"""
Test script để verify API hoạt động
Chạy: python test_api.py
"""

import requests
import json
from elasticsearch import Elasticsearch

# ============= SETUP MOCK DATA IN ELASTICSEARCH =============

def setup_mock_data():
    """Insert mock data vào Elasticsearch để test"""
    es = Elasticsearch(["http://localhost:9200"])
    
    # Mock OHLCV data
    ohlcv_data = [
        {
            "symbol": "FPT",
            "trade_date": "2024-12-20",
            "interval": "1D",
            "open": 125000.0,
            "high": 127500.0,
            "low": 124000.0,
            "close": 126500.0,
            "volume": 1500000
        },
        {
            "symbol": "FPT",
            "trade_date": "2024-12-19",
            "interval": "1D",
            "open": 124000.0,
            "high": 126000.0,
            "low": 123500.0,
            "close": 125000.0,
            "volume": 1400000
        }
    ]
    
    # Insert to ohlcv_daily_v2
    for doc in ohlcv_data:
        es.index(index="ohlcv_daily_v2", document=doc)
    
    # Mock indicators data
    indicator_data = [
        {
            "symbol": "FPT",
            "trade_date": "2024-12-20",
            "open": 125000.0,
            "high": 127500.0,
            "low": 124000.0,
            "close": 126500.0,
            "volume": 1500000,
            "vwap": 126000.0,
            "ma7": 125500.0,
            "ma30": 124000.0,
            "rsi14": 65.5,
            "daily_return": 1.2
        }
    ]
    
    # Insert to ohlcv_analysis
    for doc in indicator_data:
        es.index(index="ohlcv_analysis", document=doc)
    
    print("✓ Mock data inserted to Elasticsearch")

# ============= TEST API =============

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n=== Testing /health ===")
    r = requests.get(f"{BASE_URL}/health")
    print(f"Status: {r.status_code}")
    print(f"Response: {r.json()}")
    assert r.status_code == 200

def test_latest_price():
    """Test latest price endpoint"""
    print("\n=== Testing /ohlcv/latest/FPT ===")
    r = requests.get(f"{BASE_URL}/ohlcv/latest/FPT")
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"Symbol: {data['symbol']}")
        print(f"Close: {data['latest_data']['close']}")
        print(f"Source: {data['latest_data']['source']}")
    else:
        print(f"Error: {r.text}")

def test_historical():
    """Test historical data"""
    print("\n=== Testing /ohlcv/historical/FPT ===")
    r = requests.get(f"{BASE_URL}/ohlcv/historical/FPT?page_size=5")
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"Total records: {data['total_records']}")
        print(f"Records returned: {len(data['data'])}")
    else:
        print(f"Error: {r.text}")

def test_indicators():
    """Test indicators endpoint"""
    print("\n=== Testing /indicators/FPT/latest ===")
    r = requests.get(f"{BASE_URL}/indicators/FPT/latest")
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"RSI14: {data.get('rsi14')}")
        print(f"MA7: {data.get('ma7')}")
        print(f"MA30: {data.get('ma30')}")
    else:
        print(f"Error: {r.text}")

def test_cache():
    """Test cache behavior"""
    print("\n=== Testing Cache ===")
    
    # First request (cache miss)
    r1 = requests.get(f"{BASE_URL}/ohlcv/latest/FPT?use_cache=true")
    print(f"First request: {r1.status_code}")
    
    # Second request (cache hit)
    r2 = requests.get(f"{BASE_URL}/ohlcv/latest/FPT?use_cache=true")
    print(f"Second request: {r2.status_code}")
    print("Cache should be hit on second request")

if __name__ == "__main__":
    print("=== API Test Script ===")
    
    # Setup mock data first (nếu ES đang chạy)
    try:
        setup_mock_data()
    except Exception as e:
        print(f"⚠ Could not setup mock data: {e}")
        print("Make sure Elasticsearch is running on localhost:9200")
    
    # Run tests
    try:
        test_health()
        test_latest_price()
        test_historical()
        test_indicators()
        test_cache()
        print("\n✓ All tests completed")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")