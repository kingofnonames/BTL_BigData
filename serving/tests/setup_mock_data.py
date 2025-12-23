#!/usr/bin/env python3
"""
Mock Data Script - Insert sample data vào Elasticsearch để test Kibana
Chạy: python setup_mock_data.py
"""

from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import random

ES_HOST = "http://localhost:9200"
es = Elasticsearch([ES_HOST])

# =====================================================
# MOCK DATA GENERATORS
# =====================================================

def generate_ohlcv_data(symbol: str, days: int = 90):
    """Generate mock OHLCV data"""
    data = []
    base_price = {"FPT": 125000, "VNM": 85000, "VCB": 95000}.get(symbol, 100000)
    
    for i in range(days):
        date = (datetime.now() - timedelta(days=days-i)).strftime("%Y-%m-%d")
        
        # Random walk
        change = random.uniform(-0.03, 0.03)
        open_price = base_price
        close_price = base_price * (1 + change)
        high_price = max(open_price, close_price) * random.uniform(1.0, 1.02)
        low_price = min(open_price, close_price) * random.uniform(0.98, 1.0)
        volume = random.randint(1000000, 5000000)
        
        data.append({
            "symbol": symbol,
            "trade_date": date,
            "interval": "1D",
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "close": round(close_price, 2),
            "volume": volume
        })
        
        base_price = close_price
    
    return data

def generate_indicators(symbol: str, ohlcv_data: list):
    """Generate technical indicators from OHLCV"""
    indicators = []
    
    for i, record in enumerate(ohlcv_data):
        # Simple moving averages
        ma7 = None
        ma30 = None
        if i >= 6:
            ma7 = sum([d['close'] for d in ohlcv_data[i-6:i+1]]) / 7
        if i >= 29:
            ma30 = sum([d['close'] for d in ohlcv_data[i-29:i+1]]) / 30
        
        # RSI14
        rsi14 = random.uniform(30, 70) if i >= 13 else None
        
        # VWAP
        vwap = (record['high'] + record['low'] + record['close']) / 3
        
        # Bollinger Bands
        bollinger_upper = ma30 * 1.02 if ma30 else None
        bollinger_lower = ma30 * 0.98 if ma30 else None
        
        # Returns
        daily_return = 0
        if i > 0:
            daily_return = ((record['close'] - ohlcv_data[i-1]['close']) / 
                           ohlcv_data[i-1]['close'] * 100)
        
        indicators.append({
            "symbol": symbol,
            "trade_date": record['trade_date'],
            "open": record['open'],
            "high": record['high'],
            "low": record['low'],
            "close": record['close'],
            "volume": record['volume'],
            "vwap": round(vwap, 2),
            "ma7": round(ma7, 2) if ma7 else None,
            "ma30": round(ma30, 2) if ma30 else None,
            "bollinger_upper": round(bollinger_upper, 2) if bollinger_upper else None,
            "bollinger_lower": round(bollinger_lower, 2) if bollinger_lower else None,
            "rsi14": round(rsi14, 2) if rsi14 else None,
            "daily_return": round(daily_return, 2),
            "cumulative_return": round(daily_return * (i+1)/100, 2)
        })
    
    return indicators

def generate_market_data(index_code: str, days: int = 90):
    """Generate mock market index data"""
    data = []
    base_value = {"VNINDEX": 1250, "VN30": 1350, "HNX": 230}.get(index_code, 1000)
    
    for i in range(days):
        date = (datetime.now() - timedelta(days=days-i)).strftime("%Y-%m-%d")
        
        change = random.uniform(-0.02, 0.02)
        open_val = base_value
        close_val = base_value * (1 + change)
        high_val = max(open_val, close_val) * random.uniform(1.0, 1.01)
        low_val = min(open_val, close_val) * random.uniform(0.99, 1.0)
        volume = random.randint(500000000, 1000000000)
        
        data.append({
            "index_code": index_code,
            "trade_date": date,
            "open": round(open_val, 2),
            "high": round(high_val, 2),
            "low": round(low_val, 2),
            "close": round(close_val, 2),
            "volume": volume
        })
        
        base_value = close_val
    
    return data

# =====================================================
# INSERT TO ELASTICSEARCH
# =====================================================

def insert_data():
    """Insert all mock data to Elasticsearch"""
    
    print("=" * 60)
    print("MOCK DATA INSERTION SCRIPT")
    print("=" * 60)
    
    # Check connection
    if not es.ping():
        print("❌ Cannot connect to Elasticsearch at", ES_HOST)
        return
    
    print(f"✅ Connected to Elasticsearch: {ES_HOST}\n")
    
    # 1. OHLCV Data
    print("📊 Inserting OHLCV data...")
    symbols = ["FPT", "VNM", "VCB"]
    for symbol in symbols:
        ohlcv_data = generate_ohlcv_data(symbol, days=90)
        for record in ohlcv_data:
            es.index(index="ohlcv_daily_v2", document=record)
        print(f"   ✅ {symbol}: {len(ohlcv_data)} records")
    
    # 2. Indicators
    print("\n📈 Inserting technical indicators...")
    for symbol in symbols:
        ohlcv_data = generate_ohlcv_data(symbol, days=90)
        indicators = generate_indicators(symbol, ohlcv_data)
        for record in indicators:
            es.index(index="ohlcv_analysis", document=record)
        print(f"   ✅ {symbol}: {len(indicators)} indicators")
    
    # 3. Market Data
    print("\n🏛️  Inserting market index data...")
    indices = ["VNINDEX", "VN30", "HNX"]
    for index_code in indices:
        market_data = generate_market_data(index_code, days=90)
        for record in market_data:
            es.index(index="market_daily_v2", document=record)
        print(f"   ✅ {index_code}: {len(market_data)} records")
    
    # 4. Refresh indices
    print("\n🔄 Refreshing Elasticsearch indices...")
    es.indices.refresh(index="ohlcv_daily_v2")
    es.indices.refresh(index="ohlcv_analysis")
    es.indices.refresh(index="market_daily_v2")
    
    print("\n" + "=" * 60)
    print("✅ MOCK DATA INSERTION COMPLETED!")
    print("=" * 60)
    print("\nYou can now:")
    print("1. Access Kibana at http://localhost:5601")
    print("2. Create index patterns: ohlcv_daily_v2, ohlcv_analysis, market_daily_v2")
    print("3. Start building dashboards!")
    print("\n")

def cleanup_data():
    """Delete all mock data"""
    print("🗑️  Cleaning up mock data...")
    
    indices = ["ohlcv_daily_v2", "ohlcv_analysis", "market_daily_v2"]
    for index in indices:
        try:
            es.indices.delete(index=index)
            print(f"   ✅ Deleted index: {index}")
        except:
            print(f"   ⚠️  Index not found: {index}")
    
    print("✅ Cleanup completed!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "cleanup":
        cleanup_data()
    else:
        insert_data()
        print("💡 To cleanup, run: python setup_mock_data.py cleanup")