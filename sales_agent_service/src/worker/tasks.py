import time
from src.worker.celery_app import celery_app
from ..supabase_client import supabase

TABLE_NAME="users_data"
# Initialize the Supabase client (this will be reused in tasks)

@celery_app.task
def update_Conversation(row_Ids):
    """
    Update each row (by Id) in the Supabase table by setting 'Conversation' to 'hello'.
    After updating each row, wait for 10 seconds and then print a message indicating
    that the row has been updated.
    """
    updated_count = 0
    for row_Id in row_Ids:

        # Update the 'Conversation' column for this row
        response = (
            supabase.table(TABLE_NAME)
            .update({"Conversation": "hello"})
            .eq("Id", row_Id)
            .execute()
        )
        updated_count += 1
        time.sleep(60)

        # Print a message indicating that this row has been updated.
        print(f"Row with Id {row_Id} has been updated.")

        # Wait for 10 seconds before processing the next row.
    return f"Updated {updated_count} rows."


@celery_app.task
def process_dataset(User_id, num_workers=2):
    """
    Fetch rows from Supabase for a given user where 'Conversation' is not 'hello',
    split them into chunks for the specified number of workers, and dispatch update tasks.
    """
    result = (
            supabase.table(TABLE_NAME)
            .select("Id, User_id, Conversation")
            .eq("User_id", User_id)
            .or_("Conversation.neq.hello, Conversation.is.null")
            .execute()
        )
    rows = result.data if result.data else []


    if not rows:
        return f"No rows to process for User_id {User_id}."

    # Extract the list of Ids to update
    row_Ids = [row["Id"] for row in rows]

    # Split the list into chunks for each worker.
    # The slicing [i::num_workers] creates roughly equal partitions.
    chunks = [row_Ids[i::num_workers] for i in range(num_workers)]
    
    # Dispatch a Celery task for each chunk
    async_results = [update_Conversation.delay(chunk) for chunk in chunks if chunk]

    # Return the task Ids for reference
    return {
        "User_id": User_id,
        "total_rows": len(row_Ids)
    }
