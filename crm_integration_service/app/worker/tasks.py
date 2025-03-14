import time
from datetime import datetime
from app.worker.celery_app import celery_app
from ..supabase_client import supabase

TABLE_NAME = "Mapped_Dataset"

@celery_app.task(bind=True)
def update_Conversation(self, row_ids):
    """
    For each row:
      - Update processing start time, task_id, and status to 'processing'
      - Simulate work (replace time.sleep with your sales agent logic)
      - Update row with Conversation, status to 'success', and processing end time.
    """
    task_id = self.request.id
    for row_id in row_ids:
        # Record processing start time and mark row as processing
        start_time = datetime.utcnow().isoformat()
        supabase.table(TABLE_NAME).update({
            "processing_start_time": start_time,
            "task_id": task_id,
            "status": "processing"
        }).eq("Id", row_id).execute()

        # Simulate the sales agent work (replace this with actual logic)
        time.sleep(100)  # For testing only

        # Record processing end time and update conversation/status to success
        end_time = datetime.utcnow().isoformat()
        supabase.table(TABLE_NAME).update({
            "Conversation": "hello",
            "status": "success",
            "processing_end_time": end_time
        }).eq("Id", row_id).execute()

        print(f"Row {row_id} processed by task {task_id}: start {start_time}, end {end_time}.")

    return f"Task {task_id} processed {len(row_ids)} rows."

@celery_app.task
def process_dataset(user_id, num_agents=2):
    """
    - Fetch rows for the user where conversation is not set (or not 'hello').
    - Mark all those rows as 'pending'.
    - Split the row ids into chunks for the number of sales agents.
    - Dispatch an update_Conversation task for each chunk.
    """
    # Fetch rows for the given user that still need processing
    result = (
        supabase.table(TABLE_NAME)
        .select("Id, User_id, Conversation")
        .eq("User_id", user_id)
        .or_("status.is.null,status.in.(stopped,failure)") \
        .execute()
    )
    rows = result.data if result.data else []
    if not rows:
        return f"No rows to process for user {user_id}."

    # Get list of row IDs
    row_ids = [row["Id"] for row in rows]

    # Mark all these rows as pending
    pending_update = {"status": "pending"}
    for row_id in row_ids:
        supabase.table(TABLE_NAME).update(pending_update).eq("Id", row_id).execute()

    # Split row_ids into chunks to simulate dividing work among sales agents
    chunks = [row_ids[i::num_agents] for i in range(num_agents)]

    # Dispatch a Celery task for each non-empty chunk
    async_results = []
    for chunk in chunks:
        if chunk:
            result = update_Conversation.delay(chunk)
            async_results.append(result)

    task_ids = [r.id for r in async_results]
    print(f"Dispatched tasks for user {user_id}: {task_ids}")
    return {
        "user_id": user_id,
        "dispatched_tasks": task_ids,
        "total_rows": len(row_ids)
    }
