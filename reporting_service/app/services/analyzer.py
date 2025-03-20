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
        """Convert structured data to simple formatted text"""
        try:
            sections = []
            
            # Overview
            sections.append(response['executive_summary']['overview'])
            sections.append("")  # Empty line for spacing
            
            # KPIs
            sections.append("**Key Performance Indicators**")
            for kpi in response['executive_summary']['kpis']:
                sections.append(f"{kpi['name']}: {kpi['value']} ")
            sections.append("")  # Empty line for spacing
            
            # Top Selling Products by Region
            sections.append("**Top Selling Products by Region**")
            for region, products in response['executive_summary']['top_products_by_region'].items():
                sections.append(f"\n*{region}*")
                for product in products:
                    sections.append(f"{product['name']}: {product['sales']} ")
            sections.append("")  # Empty line for spacing
            
            # Trends
            sections.append("**Significant Trends**")
            for trend in response['executive_summary']['key_trends']:
                sections.append(trend)
            sections.append("")  # Empty line for spacing
            
            # Recommendations
            sections.append("**Strategic Recommendations**")
            for rec in response['executive_summary']['recommendations']:
                sections.append(f"*Action:* {rec['action']}")
                sections.append(f"*Rationale:* {rec['rationale']}")
                sections.append(f"*Expected Impact:* {rec['expected_impact']}")
                sections.append("")  # Empty line between recommendations
                
            return "\n".join(sections)
            
        except KeyError as e:
            logger.error(f"Summary formatting error: {str(e)}")
            return "Summary generation failed - please check raw insights"

    async def _generate_summary(self, insights: Dict) -> str:
        prompt = f"""Perform chain-of-thought analysis of this business data and generate a detailed executive summary of about 500 tokens :
        {json.dumps(insights, indent=2)}

        Follow this exact structure:
        1. Calculate Key Performance Indicators (KPIs)
        2. Identify Top Selling Products by Region (at least 1 per region)
        3. Identify Significant Trends
        4. Derive Actionable Recommendations
        5. Compose Summary

        Return JSON with:
        {{
            "chain_of_thought": {{
                "kpi_calculation": ["Calculated monthly growth rate as (current_sales - previous_sales)/previous_sales", ...],
                "trend_analysis": ["Identified 15% MoM growth in Western region", ...],
                "anomaly_detection": ["Noticed 25% sales drop in Product X during June", ...]
            }},
            "executive_summary": {{
                "overview": "Quarterly Performance Summary\\n...",
                "kpis": [
                    {{
                        "name": "Monthly Growth Rate",
                        "value": "15%",
                        "change": "+2% vs previous period"
                    }}
                ],
                "top_products_by_region": {{
                    "Western Region": [
                        {{
                            "name": "Product A",
                            "sales": "1,200",
                            "revenue": "24,000"
                        }},
                        
                    ],
                    "Eastern Region": [
                        {{
                            "name": "Product C",
                            "sales": "1,100",
                            "revenue": "22,000"
                        }},
                        
                    ]
                }},
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
        - Use formal text formatting for summary
        - KPIs must include financial and operational metrics
        - Include at least 1 top selling products for each region with sales and revenue
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