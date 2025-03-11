import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
import pandas as pd
from pathlib import Path
from main import app

client = TestClient(app)

# Path to your dataset - adjust as needed
DATASET_PATH = Path("New-SuperStore_Sales_Dataset.csv")

def test_superstore_analysis():
    """End-to-end test with real SuperStore dataset"""
    # Verify dataset exists
    if not DATASET_PATH.exists():
        pytest.fail(f"Dataset not found at {DATASET_PATH}")

    # Read and validate dataset structure
    df = pd.read_csv(DATASET_PATH)
    required_columns = ['Order Date', 'Sales', 'Profit', 'Region', 'Category']
    for col in required_columns:
        if col not in df.columns:
            pytest.fail(f"Missing required column: {col}")

    # Make API request
    with open(DATASET_PATH, "rb") as f:
        response = client.post(
            "/api/v1/analyze",
            files={"file": (DATASET_PATH.name, f, "text/csv")}
        )
    
    # Validate response
    assert response.status_code == 200
    result = response.json()
    
    # Check key insights
    assert "sales_trend" in result['insights']
    assert "regional_performance" in result['insights']
    
    # Verify predictions
    assert "next_month" in result['predictions']
    assert isinstance(result['predictions']['next_month']['forecast'], list)
    
    # Check visualizations
    assert len(result['visualizations']) >= 3  # At least 3 charts
    
    # Validate report content
    assert "recommendations" in result['executive_summary'].lower()
    assert "strategies" in result['executive_summary'].lower()

def test_superstore_report_generation():
    """Test report generation with real data"""
    with open(DATASET_PATH, "rb") as f:
        analysis_response = client.post(
            "/api/v1/analyze",
            files={"file": (DATASET_PATH.name, f, "text/csv")}
        )
    
    report_response = client.get(
        "/api/v1/report/pdf",
        params={
            "insights": analysis_response.json()["insights"],
            "predictions": analysis_response.json()["predictions"]
        }
    )
    
    assert report_response.status_code == 200
     # Real PDF should be larger