from fastapi import APIRouter, UploadFile, File, HTTPException
from services.data_processor import AdaptiveDataProcessor
from services.analyzer import BusinessAnalyzer
from services.visualizer import SmartVisualizer
from services.chatbot import BusinessChatbot
from models.schemas import AnalysisResponse
from fastapi.responses import JSONResponse, Response
from utils.json_helpers import CustomJSONEncoder
import pandas as pd
import json
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)
chatbot = BusinessChatbot()

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
        
        # Create the report dictionary
        report = {
            "schema_info": processed['schema'],
            "insights": insights,
            "chart_requirements": chart_reqs,
            "raw_data": {
                "columns": all_required_columns,
                "values": processed['df'][all_required_columns].to_dict(orient='records')
            },
            "executive_summary": insights['summary']
        }
        
        # Convert to JSON for response
        content = json.dumps(report, cls=CustomJSONEncoder)
        
        # Create a text summary for indexing instead of the full JSON
        # This will be much smaller and should index faster
        text_summary = f"""
        Analysis Report Summary
        ----------------------
        Dataset: {file.filename}
        Date: {datetime.now().isoformat()}
        
        Executive Summary:
        {insights['summary']}
        
        Key Insights:
        {'; '.join([str(insight) for insight in insights.get('key_points', [])])}
        
        Data Schema:
        {'; '.join([f"{col}: {dtype}" for col, dtype in processed['schema'].items()])}
        
        Charts Generated: {len(chart_reqs)}
        """
        
        # Store the text summary in the vector database
        try:
            await chatbot.index_report({"text": text_summary, "filename": file.filename})
            logger.info("Successfully indexed report summary in vector database")
        except Exception as e:
            logger.error(f"Failed to index report: {str(e)}")
            # Continue with the response even if indexing fails
        
        return JSONResponse(
            content=json.loads(content),
            media_type="application/json"
        )
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(500, detail=str(e))