from pydantic import BaseModel
from typing import Dict, Any, List

class AnalysisResponse(BaseModel):
    schema_info: Dict[str, Any]
    insights: Dict[str, Any]
    visualizations: List[str]
    predictions: Dict[str, Any]
    executive_summary: str