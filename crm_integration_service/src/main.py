from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os

app = FastAPI()

# File to store the received Sheets data
DATA_FILE = "sheets_data.json"

# Define request model
class SheetData(BaseModel):
    data: list  # Expects a list of lists (Google Sheets row data)

# Ensure the data file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

@app.post("/receive-data/")
async def receive_data(sheet_data: SheetData):
    """Receives Google Sheets data and stores it in a JSON file."""
    try:
        # Load existing data
        with open(DATA_FILE, "r") as f:
            existing_data = json.load(f)
        
        # Append new data
        existing_data.append(sheet_data.data)

        # Save updated data
        with open(DATA_FILE, "w") as f:
            json.dump(existing_data, f, indent=4)

        return {"message": "Data received and stored successfully!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-data/")
async def get_data():
    """Fetches stored Google Sheets data."""
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

