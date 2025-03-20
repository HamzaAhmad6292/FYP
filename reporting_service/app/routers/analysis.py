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
        visualizer = SmartVisualizer(processor)
        
        insights = await analyzer.analyze(processed['df'])
        chart_reqs = await visualizer.get_chart_requirements(processed['df'])
        
        # Prepare complete dataset for required columns
        all_required_columns = list(set(
            col for req in chart_reqs for col in req['required_columns']
        ))
        print("generated chart reqs :", chart_reqs)
        
        content = json.dumps({
            "schema_info": processed['schema'],
            "insights": insights,
            "chart_requirements": chart_reqs,
            "raw_data": {
                "columns": all_required_columns,
                "values": processed['df'][all_required_columns].to_dict(orient='records')
            },
            "executive_summary": insights['summary']
        }, cls=CustomJSONEncoder)
        
        return JSONResponse(
            content=json.loads(content),
            media_type="application/json"
        )
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(500, detail=str(e))