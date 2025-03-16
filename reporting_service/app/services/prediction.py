from prophet import Prophet
import pandas as pd
from typing import Dict

class PredictionService:
    async def forecast_sales(self, df: pd.DataFrame, periods: int = 12) -> Dict:
        """Generate sales forecast using Facebook Prophet"""
        try:
            # Prepare data for Prophet
            prophet_df = df[['Order Date', 'Sales']].rename(
                columns={'Order Date': 'ds', 'Sales': 'y'}
            )
            
            model = Prophet(interval_width=0.95)
            model.fit(prophet_df)
            
            future = model.make_future_dataframe(periods=periods)
            forecast = model.predict(future)
            
            return {
                "forecast": forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods).to_dict(),
                "model_metrics": self._calculate_metrics(prophet_df['y'], forecast['yhat'][:-periods])
            }
        except Exception as e:
            raise ValueError(f"Prediction failed: {str(e)}")
    
    def _calculate_metrics(self, actual, predicted):
        from sklearn.metrics import mean_absolute_error, r2_score
        return {
            "mae": mean_absolute_error(actual, predicted),
            "r2": r2_score(actual, predicted)
        }