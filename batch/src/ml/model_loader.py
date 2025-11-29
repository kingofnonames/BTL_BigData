import joblib
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.functions import lit, pandas_udf, PandasUDFType
from pyspark.sql.types import DoubleType
import pandas as pd
from config import Config

def load_and_predict(feature_df: DataFrame, model_path: str) -> DataFrame:
    """
    Tải mô hình đã lưu, áp dụng cho dữ liệu để tạo ra cột dự đoán.
    
    :param feature_df: DataFrame đã có các đặc trưng (features).
    :param model_path: Đường dẫn đến mô hình đã lưu.
    :return: DataFrame với cột dự đoán mới.
    """
    print("   -> Tải mô hình và thực hiện Dự đoán (Inference)...")
    
    # 1. Tải mô hình đã huấn luyện (được lưu bằng joblib)
    try:
        model = joblib.load(model_path)
    except FileNotFoundError:
        print(f"CẢNH BÁO: Không tìm thấy mô hình tại {model_path}. Sử dụng giá trị 0 cho dự đoán.")
        return feature_df.withColumn("prediction", lit(0.0).cast(DoubleType()))
    
    # 2. Feature : SMA_20, daily_return ,.... can be updated if more
    features = ['SMA_20', 'daily_return']

    @pandas_udf(DoubleType(), PandasUDFType.SCALAR)
    def predict_udf(SMA_20: pd.Series, daily_return: pd.Series) -> pd.Series:
        """Hàm dự đoán chạy trên các Worker Node của Spark."""
        X = pd.DataFrame({'SMA_20': SMA_20, 'daily_return': daily_return})
        return pd.Series(model.predict(X.fillna(0)))

    # 3. Áp dụng UDF vào DataFrame
    prediction_df = feature_df.withColumn(
        "prediction", 
        predict_udf(col('SMA_20'), col('daily_return'))
    )
    
    return prediction_df