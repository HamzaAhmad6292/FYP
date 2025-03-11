from fastapi import APIRouter, UploadFile, File, HTTPException
from services.data_processor import AdaptiveDataProcessor
from services.analyzer import BusinessAnalyzer
from services.visualizer import SmartVisualizer
from models.schemas import AnalysisResponse
from fastapi.responses import JSONResponse, Response
from utils.json_helpers import CustomJSONEncoder
import pandas as pd
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_data(file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)
        processor = AdaptiveDataProcessor()
        processed = await processor.process(df)
        
        analyzer = BusinessAnalyzer(processor)
        visualizer = SmartVisualizer(processor)  # Pass processor here
        
        insights = await analyzer.analyze(processed['df'])
        visuals = await visualizer.generate_visuals(processed['df'])
        
        content = json.dumps({
            "schema_info": processed['schema'],
            "insights": insights,
            "visualizations": visuals,
            "predictions": insights.get('forecast', {}),
            "executive_summary": insights['summary']
        }, cls=CustomJSONEncoder)
        
        return JSONResponse(
            content=json.loads(content),
            media_type="application/json"
        )
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(500, detail=str(e))