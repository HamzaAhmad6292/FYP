from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi import FastAPI, Request,Query

import json
import os
from .helper_function import create_table_for_new_user,add_data_to_user_dataset,map_and_insert_dataset
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
        response=create_table_for_new_user(user_id)


        if response=="ok":
            dataset_response=add_data_to_user_dataset(user_id,user_dataset)
        
        response=map_and_insert_dataset(user_dataset=user_dataset,user_id=user_id)




        if response:
            return {"message": "Data received and stored successfully!","response":dataset_response}
        else:
            return{"masla":"matter hogia boss"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-data/")
async def get_user_data(user_id: int = Query(..., description="User ID to fetch data")):
    """Fetches stored Google Sheets data for a specific user."""

    try:
        # Fetch user data from the Supabase table
        response = supabase.table(f"dataset_{str(user_id)}").select("*").execute()

        # Check if there was an error
        if not response:
            raise HTTPException(status_code="404", detail=f"Error fetching data: {response.data}")

        return {"data": response.data}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/get-mapped-data/")
async def get_mapped_user_data(user_id: int = Query(..., description="User ID to fetch mapped data")):
    """Fetches stored Google Sheets data for a specific user."""

    try:
        # Fetch user data from the Supabase table
        response = supabase.table("Mapped_Dataset").select("*").eq("User_id", user_id).execute()

        # Check if there was an error
        if not response:
            raise HTTPException(status_code="404", detail=f"Error fetching data: {response.data}")

        return {"data": response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


