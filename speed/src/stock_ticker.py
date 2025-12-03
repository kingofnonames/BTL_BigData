from pydantic import BaseModel, Field

class StockTicker(BaseModel):
    """
    Model đại diện cho một bản ghi giao dịch chứng khoán (ticker) từ Kafka.
    """
    symbol: str = Field(..., min_length=2, max_length=10, description="Mã cổ phiếu (VD: FPT, VNM)")
    price: float = Field(..., gt=0, description="Giá giao dịch (phải lớn hơn 0)")
    volume: int = Field(..., ge=0, description="Khối lượng giao dịch (lớn hơn hoặc bằng 0)")
    timestamp: int = Field(..., description="Thời gian giao dịch dưới dạng Unix epoch (giây hoặc mili giây)")
    exchange: str = Field(..., description="Sàn giao dịch (VD: HOSE, HNX)")

    class Config:
        extra = 'ignore'