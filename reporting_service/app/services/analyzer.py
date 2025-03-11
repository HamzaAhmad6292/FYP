from prophet import Prophet
import pandas as pd
from services.llm_service import LLMService
import logging
import json
from typing import Dict

logger = logging.getLogger(__name__)

class BusinessAnalyzer:
    def __init__(self, processor):
        self.processor = processor
        self.llm = LLMService()
    
    async def analyze(self, df: pd.DataFrame) -> Dict:
        insights = {
            "forecast": await self._generate_forecast(df),
            "trends": await self._detect_trends(df),
            "segments": await self._identify_segments(df)  # Added this line
        }
        insights["summary"] = await self._generate_summary(insights)
        return insights

    # Add these missing methods
    async def _identify_segments(self, df: pd.DataFrame) -> Dict:
        """LLM-powered customer/product segmentation"""
        prompt = f"""Analyze this data for market segments:
        {df.head().to_markdown()}
        
        Return JSON with:
        - top_product_segments: list
        - regional_performance: dict
        - customer_segments: list
        """
        return await self.llm.generate(prompt)
    
    def _format_summary(self, response: Dict) -> str:
        """Convert structured data to markdown"""
        try:
            md = []
            # Header
            md.append(f"# Executive Summary\n{response['executive_summary']['overview']}")
            
            # KPIs
            md.append("## Key Performance Indicators")
            md.append("| Metric | Value | Change |\n|--------|-------|--------|")
            for kpi in response['executive_summary']['kpis']:
                md.append(f"| {kpi['name']} | {kpi['value']} | {kpi['change']} |")
            
            # Trends
            md.append("\n## Significant Trends")
            md.extend([f"- {trend}" for trend in response['executive_summary']['key_trends']])
            
            # Recommendations
            md.append("\n## Strategic Recommendations")
            for rec in response['executive_summary']['recommendations']:
                md.append(f"### {rec['action']}\n**Rationale**: {rec['rationale']}\n**Expected Impact**: {rec['expected_impact']}\n")
                
            return "\n".join(md)
            
        except KeyError as e:
            logger.error(f"Summary formatting error: {str(e)}")
            return "## Executive Summary\nSummary generation failed - please check raw insights"

    async def _generate_summary(self, insights: Dict) -> str:
        prompt = f"""Perform chain-of-thought analysis of this business data and generate executive summary:
        {json.dumps(insights, indent=2)}

        Follow this exact structure:
        1. Calculate Key Performance Indicators (KPIs)
        2. Identify Significant Trends
        3. Derive Actionable Recommendations
        4. Compose Summary

        Return JSON with:
        {{
            "chain_of_thought": {{
                "kpi_calculation": ["Calculated monthly growth rate as (current_sales - previous_sales)/previous_sales", ...],
                "trend_analysis": ["Identified 15% MoM growth in Western region", ...],
                "anomaly_detection": ["Noticed 25% sales drop in Product X during June", ...]
            }},
            "executive_summary": {{
                "overview": "### Quarterly Performance Summary\\n...",
                "kpis": [
                    {{
                        "name": "Monthly Growth Rate",
                        "value": "15%",
                        "change": "+2% vs previous period"
                    }}
                ],
                "key_trends": [
                    "Western region driving 60% of total growth",
                    "Category A products underperforming by 20%"
                ],
                "recommendations": [
                    {{
                        "action": "Increase inventory in Western region",
                        "rationale": "15% higher growth vs other regions",
                        "expected_impact": "2-5% additional revenue"
                    }}
                ]
            }}
        }}
        
        Requirements:
        - Use markdown formatting for summary
        - KPIs must include financial and operational metrics
        - Recommendations must tie directly to trends
        - Maintain professional business tone
        - Quantify all claims with data points
        - Highlight risks and opportunities
        """
        
        response = await self.llm.generate(prompt)
        return self._format_summary(response)
    
    
    async def _generate_forecast(self, df: pd.DataFrame) -> Dict:
        try:
            model = Prophet()
            prophet_df = df.rename(columns={
                self.processor.schema['date_columns'][0]: 'ds',
                self.processor.schema['value_columns'][0]: 'y'
            })
            model.fit(prophet_df)
            future = model.make_future_dataframe(periods=30)
            forecast = model.predict(future)
            
            # Convert Timestamps to ISO strings
            forecast['ds'] = forecast['ds'].dt.strftime('%Y-%m-%d')
            return forecast[['ds', 'yhat']].tail().to_dict()
            
        except Exception as e:
            logger.error(f"Forecasting failed: {str(e)}")
            return {}

    async def _detect_trends(self, df: pd.DataFrame) -> Dict:
        prompt = f"""Analyze trends in this data:
        {df.head().to_markdown()}
        Return JSON with trend analysis"""
        return await self.llm.generate(prompt)