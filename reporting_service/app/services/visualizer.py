# services/visualizer.py
from services.llm_service import LLMService
import logging
from typing import Dict, List
import pandas as pd

logger = logging.getLogger(__name__)

class SmartVisualizer:
    def __init__(self, processor):
        self.llm = LLMService()
        self.processor = processor

    async def get_chart_requirements(self, df: pd.DataFrame) -> List[Dict]:
        """Get chart types and required columns"""
        specs = await self._get_visualization_specs(df)
        return [self._extract_columns(spec) for spec in specs]

    async def _get_visualization_specs(self, df: pd.DataFrame) -> list:
        """Get visualization specs with LLM"""
        prompt = f"""Analyze this dataset and suggest atleast 4 visualizations from [line, bar, pie, stacked line chart, donut, sales to product distribution ]:
        Columns: {df.columns.tolist()}
        Sample Data: {df.head(10).to_dict()}
        Statistical Information of Data : {df.describe().to_dict()}
        
        Return JSON format:
        {{
            "charts": [
                {{
                    "type": "line|bar|pie|stacked line|donut|sales to product distribution",
                    "required_columns": ["col1", "col2"],
                    "chart_purpose": "Show sales trends over time"
                }}
            ]
        }}"""
        
        response = await self.llm.generate(prompt)
        return response.get('charts', [])

    def _extract_columns(self, spec: Dict) -> Dict:
        """Extract column requirements from spec"""
        return {
            "chart_type": spec.get('type', 'unknown'),
            "required_columns": spec.get('required_columns', []),
            "purpose": spec.get('chart_purpose', '')
        }