import pandas as pd
import logging
from typing import Dict, Any
from services.llm_service import LLMService

logger = logging.getLogger(__name__)

class AdaptiveDataProcessor:
    def __init__(self):
        self.llm = LLMService()
        self.schema = {}
    
    async def process(self, df: pd.DataFrame) -> Dict:
        try:
            self.schema = await self._analyze_structure(df)
            df = self._standardize_data(df)
            return {"df": df, "schema": self.schema}
        except Exception as e:
            logger.error(f"Processing failed: {str(e)}")
            raise
    
    async def _analyze_structure(self, df: pd.DataFrame) -> Dict:
        prompt = f"""Analyze this dataset structure and return JSON with:
        {{
            "date_columns": ["col1", "col2"],
            "value_columns": ["col3"],
            "entity_columns": {{
                "products": ["col4"],
                "geography": ["col5"]
            }},
            "required_transformations": [
                {{"type": "datetime", "column": "col1", "format": "auto"}},
                {{"type": "normalize", "column": "col3"}}
            ]
        }}
        
        Dataset Sample:
        {df.head(3).to_markdown()}
        Columns: {df.columns.tolist()}
        """
        return await self.llm.generate(prompt)
    
    def _standardize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        # Apply transformations from schema
        if 'required_transformations' in self.schema:
            for transform in self.schema['required_transformations']:
                if transform['type'] == 'datetime':
                    df[transform['column']] = pd.to_datetime(
                        df[transform['column']], errors='coerce'
                    )
        return df