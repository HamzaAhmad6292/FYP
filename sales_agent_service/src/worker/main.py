# src/main.py

import sys
from src.worker.tasks import process_dataset

if __name__ == "__main__":
    # Get the user_id and number of worker chunks from command line arguments
    if len(sys.argv) < 2:
        print("Usage: python src/main.py <user_id> [num_workers]")
        sys.exit(1)
    
    user_id = sys.argv[1]
    num_workers = int(sys.argv[2]) if len(sys.argv) > 2 else 1

    result = process_dataset.delay(user_id, num_workers)
    print(f"Processing task for user {user_id} dispatched with Task ID:", result.id)
