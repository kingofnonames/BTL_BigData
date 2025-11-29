import pandas as pd
from pyspark.sql.dataframe import DataFrame
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import joblib

def train_and_save_model(spark_df: DataFrame, save_path: str):
    """
    Thu thập dữ liệu, huấn luyện mô hình Scikit-learn và lưu lại.
    (Chỉ nên chạy nếu K8s Job được cấu hình để huấn luyện).
    """
    print("   -> Bắt đầu Huấn luyện Mô hình...")

    # 1. Lấy mẫu và chuyển đổi sang Pandas (Scikit-learn)
    pandas_df = spark_df.sample(False, 0.1).toPandas() 
    
    # 2. Chuẩn bị dữ liệu
    features = ['SMA_20', 'daily_return']
    target = 'close'
    
    X = pandas_df[features].fillna(0)
    y = pandas_df[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 3. Huấn luyện Mô hình
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # 4. Đánh giá
    predictions = model.predict(X_test)
    rmse = mean_squared_error(y_test, predictions, squared=False)
    print(f"   -> RMSE của mô hình: {rmse}")
    
    # 5. Lưu mô hình
    joblib.dump(model, save_path)
    print(f"   -> Mô hình đã được lưu tại: {save_path}")