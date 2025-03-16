from fastapi import APIRouter, HTTPException
from services.prediction import PredictionService
from services.data_processor import DataProcessor
from models.schemas import AnalysisRequest
from typing import Dict

router = APIRouter(tags=["Predictions"])

@router.post("/forecast")
async def get_predictions(request: AnalysisRequest) -> Dict:
    try:
        processor = DataProcessor()
        df, _ = await processor.process_data(request.file_path)
        
        forecast_periods = {
            'next_month': 1,
            'next_quarter': 3,
            'next_year': 12
        }.get(request.forecast_period, 1)
        
        predictions = await PredictionService().forecast_sales(df, forecast_periods)
        return {
            "status": "success",
            "forecast": predictions['forecast'],
            "confidence_interval": 0.95
        }
    except Exception as e:
        raise HTTPException(500, str(e))