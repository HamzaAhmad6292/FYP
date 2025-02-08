from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi import FastAPI, Request

import json
import os
from .helper_function import create_table_for_newUser,add_data_to_userDataset
from ..supabase_client import supabase
app = FastAPI()

# File to store the received Sheets data
DATA_FILE = "sheets_data.json"

# Define request model
# class SheetData(BaseModel):
#     data: list  

# Ensure the data file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

@app.post("/receive_data")
async def receive_data(user_data:Request):
    data = await user_data.json()
    user_id=data.get("user_id")
    user_dataset=data.get("dataset")

    try:
        print(user_id)
        # Load existing data
        response=create_table_for_newUser(user_id,user_dataset)
        print("response"+response)    
        with open(DATA_FILE, "r") as f:
            existing_data = json.load(f)
        
        
        existing_data.append(user_data.dataset)

        if response:
            dataset_response=add_data_to_userDataset(user_dataset)


        # Save updated data
        with open(DATA_FILE, "w") as f:
            json.dump(existing_data, f, indent=4)

        if dataset_response:
            return {"message": "Data received and stored successfully!","response":dataset_response}
        else:
            return{"masla":"matter hogia boss"}

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

