"""
Crawler để thu thập dữ liệu phân tích cơ bản (Fundamental Analysis)
Bao gồm: báo cáo tài chính, chỉ số tài chính, thông tin doanh nghiệp
"""
from vnstock import Vnstock
import pandas as pd
from datetime import datetime
import os

class FundamentalCrawler:
    def __init__(self, symbol):
        self.symbol = symbol.upper()
        self.stock = Vnstock().stock(symbol=self.symbol, source='VCI')
        
    def get_company_profile(self):
        """Lấy thông tin tổng quan công ty"""
        try:
            print(f"\n[{self.symbol}] Đang lấy thông tin công ty...")
            # Sử dụng overview() thay vì profile()
            profile = self.stock.company.overview()
            return profile
        except Exception as e:
            print(f"Lỗi khi lấy thông tin công ty: {e}")
            return None
    
    def get_financial_report(self, report_type='BalanceSheet', period='year', limit=5):
        """
        Lấy báo cáo tài chính
        report_type: 'BalanceSheet' (BCĐKT), 'IncomeStatement' (KQKD), 'CashFlow' (LCTT)
        period: 'year' (năm), 'quarter' (quý)
        """
        try:
            print(f"\n[{self.symbol}] Đang lấy {report_type} theo {period}...")
            
            if report_type == 'BalanceSheet':
                data = self.stock.finance.balance_sheet(period=period, lang='vi')
            elif report_type == 'IncomeStatement':
                data = self.stock.finance.income_statement(period=period, lang='vi')
            elif report_type == 'CashFlow':
                data = self.stock.finance.cash_flow(period=period, lang='vi')
            else:
                print(f"Loại báo cáo không hợp lệ: {report_type}")
                return None
            
            return data.head(limit) if data is not None else None
        except Exception as e:
            print(f"Lỗi khi lấy báo cáo tài chính: {e}")
            return None
    
    def get_financial_ratios(self, period='year', limit=5):
        """Lấy các chỉ số tài chính"""
        try:
            print(f"\n[{self.symbol}] Đang lấy chỉ số tài chính...")
            ratios = self.stock.finance.ratio(period=period, lang='vi')
            return ratios.head(limit) if ratios is not None else None
        except Exception as e:
            print(f"Lỗi khi lấy chỉ số tài chính: {e}")
            return None
    
    def get_dividends(self):
        """Lấy lịch sử chia cổ tức"""
        try:
            print(f"\n[{self.symbol}] Đang lấy lịch sử cổ tức...")
            dividends = self.stock.finance.dividend()
            return dividends
        except Exception as e:
            print(f"Lỗi khi lấy lịch sử cổ tức: {e}")
            return None
    
    def save_data(self, data, filename):
        """Lưu dữ liệu vào file CSV"""
        if data is None or data.empty:
            print(f"Không có dữ liệu để lưu cho {filename}")
            return False
        
        try:
            # Tạo thư mục data nếu chưa có
            os.makedirs('data/fundamental', exist_ok=True)
            
            filepath = f"data/fundamental/{filename}"
            data.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"✓ Đã lưu: {filepath}")
            return True
        except Exception as e:
            print(f"Lỗi khi lưu file: {e}")
            return False

def main():
    # Thiết lập tham số
    symbol = 'FPT'
    
    print(f"{'='*60}")
    print(f"BẮT ĐẦU THU THẬP DỮ LIỆU FUNDAMENTAL - {symbol}")
    print(f"{'='*60}")
    
    # Khởi tạo crawler
    crawler = FundamentalCrawler(symbol)
    
    # 1. Thông tin công ty
    profile = crawler.get_company_profile()
    if profile is not None:
        print("\n--- Thông tin công ty ---")
        print(profile)
        crawler.save_data(profile, f"{symbol}_profile_{datetime.now().strftime('%Y%m%d')}.csv")
    
    # 2. Báo cáo tài chính
    for report_type in ['BalanceSheet', 'IncomeStatement', 'CashFlow']:
        for period in ['year', 'quarter']:
            data = crawler.get_financial_report(report_type, period, limit=5)
            if data is not None:
                print(f"\n--- {report_type} ({period}) ---")
                print(data.head())
                crawler.save_data(
                    data, 
                    f"{symbol}_{report_type}_{period}_{datetime.now().strftime('%Y%m%d')}.csv"
                )
    
    # 3. Chỉ số tài chính
    for period in ['year', 'quarter']:
        ratios = crawler.get_financial_ratios(period, limit=5)
        if ratios is not None:
            print(f"\n--- Chỉ số tài chính ({period}) ---")
            print(ratios.head())
            crawler.save_data(
                ratios,
                f"{symbol}_ratios_{period}_{datetime.now().strftime('%Y%m%d')}.csv"
            )
    
    # 4. Lịch sử cổ tức
    dividends = crawler.get_dividends()
    if dividends is not None:
        print("\n--- Lịch sử cổ tức ---")
        print(dividends.head())
        crawler.save_data(
            dividends,
            f"{symbol}_dividends_{datetime.now().strftime('%Y%m%d')}.csv"
        )
    
    print(f"\n{'='*60}")
    print("HOÀN THÀNH!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()