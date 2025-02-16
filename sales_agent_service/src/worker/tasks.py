# src/worker/tasks.py

import time
from worker.celery_app import celery_app
from ..supabase_client import supabase
TABLE_NAME="users_data"
USER_ID="1212"

@celery_app.task
def update_conversation(row_ids):
    """
    Update each row (by id) in the Supabase table by setting 'conversation' to 'hello'.
    """
    updated_count = 0
    for row_id in row_ids:
        response = (
            supabase.table(TABLE_NAME)
            .update({"conversation": "hello"})
            .eq("id", row_id)
            .execute()
        )
        # Optional: log response or check for errors
        updated_count += 1
        # Simulate processing time (remove in production)
        time.sleep(0.5)
    return f"Updated {updated_count} rows."

@celery_app.task
def process_dataset(num_workers=2):
    """
    Fetch rows from Supabase that haven't been updated (i.e. where conversation is not 'hello'),
    split them into chunks for the specified number of workers, and dispatch update tasks.
    """
    # Fetch rows where 'conversation' is not 'hello' (assuming unprocessed rows have null/other value)
    result = supabase.table(TABLE_NAME).select("id, conversation").neq("conversation", "hello").execute()
    rows = result.data if result.data else []

    if not rows:
        return "No rows to process."

    # Extract the list of IDs to update
    row_ids = [row["id"] for row in rows]

    # Split the list into chunks for each worker.
    # The slicing [i::num_workers] creates roughly equal partitions.
    chunks = [row_ids[i::num_workers] for i in range(num_workers)]
    
    # Dispatch a Celery task for each chunk
    async_results = [update_conversation.delay(chunk) for chunk in chunks if chunk]

    # Return the task IDs for reference (the frontend could poll the backend or check Supabase)
    return {"dispatched_tasks": [res.id for res in async_results]}
