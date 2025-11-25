"""
Utilities để lưu trữ và quản lý dữ liệu
"""
import pandas as pd
import os
from datetime import datetime

class DataSaver:
    def __init__(self, base_dir='data'):
        """Khởi tạo DataSaver với thư mục gốc"""
        self.base_dir = base_dir
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Tạo các thư mục cần thiết"""
        directories = [
            f'{self.base_dir}/ohlcv',
            f'{self.base_dir}/fundamental',
            f'{self.base_dir}/technical',
            f'{self.base_dir}/market',
            f'{self.base_dir}/raw'
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def save_csv(self, data, filename, subdirectory='raw', index=True):
        """
        Lưu DataFrame vào file CSV
        
        Args:
            data: DataFrame cần lưu
            filename: Tên file
            subdirectory: Thư mục con (ohlcv, fundamental, technical, market, raw)
            index: Có lưu index hay không
        """
        if data is None or data.empty:
            print(f"⚠ Không có dữ liệu để lưu cho {filename}")
            return False
        
        try:
            filepath = os.path.join(self.base_dir, subdirectory, filename)
            data.to_csv(filepath, index=index, encoding='utf-8-sig')
            print(f"✓ Đã lưu: {filepath} ({len(data)} dòng)")
            return True
        except Exception as e:
            print(f"✗ Lỗi khi lưu file {filename}: {e}")
            return False
    
    def save_multiple(self, data_dict, subdirectory='raw', index=True):
        """
        Lưu nhiều DataFrame cùng lúc
        
        Args:
            data_dict: Dictionary với key là tên file, value là DataFrame
            subdirectory: Thư mục con
            index: Có lưu index hay không
        """
        results = {}
        for filename, data in data_dict.items():
            results[filename] = self.save_csv(data, filename, subdirectory, index)
        return results
    
    def load_csv(self, filename, subdirectory='raw'):
        """Đọc file CSV"""
        try:
            filepath = os.path.join(self.base_dir, subdirectory, filename)
            data = pd.read_csv(filepath, encoding='utf-8-sig')
            print(f"✓ Đã đọc: {filepath} ({len(data)} dòng)")
            return data
        except Exception as e:
            print(f"✗ Lỗi khi đọc file {filename}: {e}")
            return None
    
    def list_files(self, subdirectory='raw', extension='.csv'):
        """Liệt kê các file trong thư mục"""
        try:
            directory = os.path.join(self.base_dir, subdirectory)
            files = [f for f in os.listdir(directory) if f.endswith(extension)]
            return sorted(files)
        except Exception as e:
            print(f"✗ Lỗi khi liệt kê file: {e}")
            return []
    
    def get_file_info(self, subdirectory='raw'):
        """Lấy thông tin về các file đã lưu"""
        files = self.list_files(subdirectory)
        info = []
        
        for file in files:
            filepath = os.path.join(self.base_dir, subdirectory, file)
            size = os.path.getsize(filepath)
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            info.append({
                'filename': file,
                'size_kb': round(size / 1024, 2),
                'modified': mtime.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return pd.DataFrame(info)

def main():
    """Demo sử dụng DataSaver"""
    saver = DataSaver()
    
    # Tạo dữ liệu mẫu
    sample_data = pd.DataFrame({
        'date': pd.date_range(start='2024-01-01', periods=5),
        'open': [100, 102, 101, 103, 105],
        'high': [105, 106, 104, 107, 108],
        'low': [98, 100, 99, 102, 103],
        'close': [102, 101, 103, 105, 106],
        'volume': [1000000, 1200000, 950000, 1100000, 1300000]
    })
    
    # Lưu file
    filename = f"DEMO_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    saver.save_csv(sample_data, filename, subdirectory='raw', index=False)
    
    # Liệt kê files
    print("\n--- Danh sách files ---")
    files = saver.list_files('raw')
    for f in files:
        print(f"  - {f}")
    
    # Thông tin chi tiết
    print("\n--- Chi tiết files ---")
    info = saver.get_file_info('raw')
    print(info)

if __name__ == "__main__":
    main()   