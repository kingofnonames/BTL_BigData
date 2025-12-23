from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta
import random
from models.schemas import StockPrediction, PredictionModel
from api.dependencies import get_lambda_merger

router = APIRouter(prefix="/predictions", tags=["Predictions"])

@router.get("/{symbol}", response_model=StockPrediction)
async def get_predictions(
    symbol: str,
    merger=Depends(get_lambda_merger)
):
    """
    Get ML predictions - Currently MOCK
    TODO: Replace with real predictions from mlib_evaluate job
    """
    symbol = symbol.upper()
    
    # Get latest price for base
    latest = merger.get_latest_price(symbol)
    
    if not latest:
        raise HTTPException(status_code=404, detail=f"No data for predictions: {symbol}")
    
    current_close = float(latest['close'])
    prediction_date = latest['trade_date']
    
    # Parse date and add 1 day
    pred_date_obj = datetime.strptime(prediction_date, "%Y-%m-%d")
    target_date = (pred_date_obj + timedelta(days=1)).strftime("%Y-%m-%d")
    
    # MOCK predictions
    mock_prediction = StockPrediction(
        symbol=symbol,
        prediction_date=prediction_date,
        target_date=target_date,
        current_close=current_close,
        predictions=[
            PredictionModel(
                model_name="linear_regression",
                predicted_close=current_close * (1 + random.uniform(-0.02, 0.02)),
                rmse=current_close * 0.012
            ),
            PredictionModel(
                model_name="random_forest",
                predicted_close=current_close * (1 + random.uniform(-0.015, 0.015)),
                rmse=current_close * 0.009
            )
        ]
    )
    
    return mock_prediction

@router.get("/models/status")
async def get_models_status():
    """Get status of all models"""
    return {
        "total_models": 2,
        "models": [
            {
                "name": "linear_regression",
                "status": "active",
                "last_trained": "2024-12-01"
            },
            {
                "name": "random_forest",
                "status": "active",
                "last_trained": "2024-12-01"
            }
        ]
    }