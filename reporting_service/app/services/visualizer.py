# services/visualizer.py
import plotly.express as px
from services.llm_service import LLMService
import logging
from typing import Dict, Any, Optional, List
import pandas as pd

logger = logging.getLogger(__name__)

class SmartVisualizer:
    def __init__(self, processor):
        self.llm = LLMService()
        self.processor = processor

    async def generate_visuals(self, df: pd.DataFrame) -> List[str]:
        """Ensure only valid JSON strings are returned"""
        specs = await self._get_visualization_specs(df)
        charts = [self._create_chart(df, spec) for spec in specs]
        return [chart for chart in charts if chart is not None]

    async def _get_visualization_specs(self, df: pd.DataFrame) -> list:
        """Get visualization specs with LLM"""
        prompt = f"""Generate 3-5 visualization specs for this business data:
        Columns: {df.columns.tolist()}
        Sample Data: {df.head(5).to_dict()}
        
        Return JSON format:
        {{
            "charts": [
                {{
                    "type": "line|bar|pie",
                    "title": "Chart Title",
                    "x": "column_name",
                    "y": "column_name",
                    "color": "column_name (optional)",
                    "aggregation": "sum|mean|count"
                }}
            ]
        }}"""
        
        response = await self.llm.generate(prompt)
        return response.get('charts', [])

    def _create_chart(self, df: pd.DataFrame, spec: Dict) -> Optional[str]:
        """Handle chart-specific parameters"""
        try:
            chart_type = spec.get('type', 'line')
            params = {
                'title': spec.get('title', f"{chart_type.capitalize()} Chart"),
                'labels': {'x': '', 'y': ''}
            }

            # Chart-type specific parameter handling
            if chart_type == 'pie':
                params['names'] = spec.get('x', 'category')
                params['values'] = spec.get('y', 'value')
            else:
                params['x'] = spec.get('x', 'date')
                params['y'] = spec.get('y', 'value')
                if 'color' in spec:
                    params['color'] = spec['color']

            # Handle aggregation
            agg_column = params['values'] if chart_type == 'pie' else params['y']
            if spec.get('aggregation'):
                agg_df = df.groupby(params.get('x') or params.get('names')).agg(
                    {agg_column: spec['aggregation']}
                ).reset_index()
            else:
                agg_df = df

            fig = getattr(px, chart_type)(agg_df, **params)
            return fig.to_json()
            
        except Exception as e:
            logger.error(f"Chart creation failed: {str(e)}")
            return None

    def _create_fallback_chart(self, df: pd.DataFrame):
        """Default chart when others fail"""
        return px.line(df, 
                      x=self.processor.schema['date_columns'][0],
                      y=self.processor.schema['value_columns'][0],
                      title="Sales Trend").to_json()