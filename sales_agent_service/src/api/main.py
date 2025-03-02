from fastapi import FastAPI, BackgroundTasks
from celery.result import AsyncResult
from src.worker.tasks import process_dataset
from src.worker.celery_app import celery_app  # Import celery_app

app = FastAPI()

# Dictionary to store active tasks per user
active_tasks = {}
@app.post("/start-processing")
async def start_processing(user_id: str, num_agents: int):
    """
    Starts processing the dataset for a given user_id and number of sales agents.
    """
    try:
        if user_id in active_tasks:
            return {"message": "Processing is already running for this user."}
        
        # Start the Celery task
        task = process_dataset.delay(user_id, num_agents)
        
        # Store task ID
        active_tasks[user_id] = task.id

        return {"message": "Processing started", "task_id": task.id}
    except Exception as e:
        # Optionally log the exception here
        return {"message": f"An error occurred while starting processing: {str(e)}"}


@app.post("/stop-processing")
async def stop_processing(user_id: str):
    """
    Stops processing for a given user_id by revoking the Celery task.
    """
    try:
        if user_id not in active_tasks:
            return {"message": "No active processing for this user."}

        # Get task ID and revoke it
        task_id = active_tasks.pop(user_id, None)
        if task_id:
            AsyncResult(task_id).revoke(terminate=True)
            return {"message": "Processing stopped", "task_id": task_id}
        
        return {"message": "Failed to stop processing"}
    except Exception as e:
        # Optionally log the exception here
        return {"message": f"An error occurred while stopping processing: {str(e)}"}


@app.get("/status/{user_id}")
async def check_status(user_id: str):
    """
    Checks the status of the processing task for a user.
    """
    try:
        if user_id not in active_tasks:
            return {"message": "No active task for this user."}

        task_id = active_tasks[user_id]
        task = AsyncResult(task_id)

        return {"user_id": user_id, "task_id": task_id, "status": task.status}
    except Exception as e:
        # Optionally log the exception here
        return {"message": f"An error occurred while checking status: {str(e)}"}
