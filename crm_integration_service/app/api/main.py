from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi import FastAPI, Request,Query

import json
import os
from .helper_function import create_table_for_new_user,add_data_to_user_dataset,map_and_insert_dataset
from ..supabase_client import supabase
from fastapi import FastAPI
from celery.result import AsyncResult
from app.worker.tasks import process_dataset
from app.worker.celery_app import celery_app
from app.supabase_client import supabase  # Adjust this import to match your client module


app = FastAPI()

@app.post("/receive_data")
async def receive_data(user_data:Request):
    data = await user_data.json()
    user_id=data.get("user_id")
    user_dataset=data.get("dataset")
    file_name=data.get("filen_name")

    try:
        print(user_id)
        # Load existing data
        response=create_table_for_new_user(user_id)


        if response=="ok":
            dataset_response=add_data_to_user_dataset(user_id,user_dataset)
        
        response=map_and_insert_dataset(user_dataset=user_dataset,user_id=user_id,file_name=file_name)




        if response:
            return {"message": "Data received and stored successfully!","response":dataset_response}
        else:
            return{"masla":"matter hogia boss"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-user-data/")
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
    

@app.get("/get-user-mapped-data/")
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
    









@app.post("/start-processing")
async def start_processing(user_id: str, num_agents: int):
    """
    Starts processing for a given user by:
      1. Checking if there are any rows in a pending or processing state.
      2. If not, initiating the Celery task (process_dataset) which marks rows as pending.
    """
    # Query for any rows already in 'pending' or 'processing' status for this user
    query = supabase.table("users_data") \
                    .select("task_id") \
                    .eq("User_id", user_id) \
                    .or_("status.is.null,status.in.(stopped,failure)") \
                    .execute()


    if query.data and len(query.data) == 0:
        return {"message": "Processing is already running for this user."}
    
    # Start the Celery task that processes the dataset for the user
    task = process_dataset.delay(user_id, num_agents)
    
    return {"message": "Processing started", "task_id": task.id}


@app.post("/stop-processing")
async def stop_processing(user_id: str):
    """
    Stops processing for a given user by:
      1. Querying the table for rows with status 'pending' or 'processing'.
      2. Collecting distinct task_ids from those rows.
      3. Revoking each of the tasks.
      4. Updating the rows in the database to mark them as 'stopped'.
    """
    # Retrieve rows for this user with status pending or processing
    query = supabase.table("users_data") \
                    .select("task_id") \
                    .eq("User_id", user_id) \
                    .in_("status", ["pending", "processing"]) \
                    .execute()
    
    if not query.data or len(query.data) == 0:
        return {"message": "No active processing for this user."}

    # Get distinct, non-null task IDs
    task_ids = list({row["task_id"] for row in query.data if row.get("task_id")})
    
    if not task_ids:
        return {"message": "No active task ids found for this user."}

    # Revoke each task using Celery's AsyncResult
    for task_id in task_ids:
        AsyncResult(task_id).revoke(terminate=True)
    
    # Optionally update the rows to mark them as stopped
    supabase.table("users_data") \
            .update({"status": "stopped"}) \
            .eq("User_id", user_id) \
            .in_("status", ["pending", "processing"]) \
            .execute()

    return {"message": "Processing stopped", "task_ids": task_ids}


@app.get("/status/{user_id}")
async def check_status(user_id: str):
    """
    Returns all rows for the given user that are in a 'pending' state.
    You can modify the query if you'd like to include other statuses (e.g., 'processing').
    """
    query = supabase.table("users_data") \
                    .select("*") \
                    .eq("User_id", user_id) \
                    .eq("status", "pending") \
                    .execute()
    
    return {"pending_rows": query.data}

    




