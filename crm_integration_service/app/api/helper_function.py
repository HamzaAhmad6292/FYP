from ..supabase_client import supabase
from fastapi import HTTPException
import pandas as pd
import psycopg2
import logging
from ..data_pipeline.DatasetMapper import DatasetMapper


# Database connection string
PSQL_URL = "postgresql://postgres:hamzathegreat1234@db.gtizhtnrlztkccysrtkg.supabase.co:5432/postgres"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def map_and_insert_dataset(user_dataset, user_id):
    try:
        logging.info("Loading mapping rules from app/utils/mapping_rules.json")
        mapping_rules = pd.read_json('app/utils/mapping_rules.json')
        logging.debug(f"Mapping rules loaded: {mapping_rules}")

        mapper = DatasetMapper(rules_path="app/utils/mapping_rules.json")
        
        logging.info("Mapping dataset using the provided mapping rules.")
        mapped_dataset,_ = mapper.map_dataset(user_dataset)
        logging.debug(f"Mapped dataset: {mapped_dataset}")

        mapped_dataset["User_id"] = user_id
        logging.info("User ID added to the mapped dataset.")

        json_compatible_dataset = mapped_dataset.to_dict(orient='records')
        print(mapping_rules)
        logging.info(f"Inserting mapped dataset for user_id {user_id} into Supabase.")
        response = supabase.table("Mapped_Dataset").insert(json_compatible_dataset).execute()
        print(f"response:{response}")

        if  not response:
            raise Exception(f"Error inserting Mapped dataset: {response['detail']}")
        
        # Log success
        logging.info(f"Dataset inserted successfully for user_id {user_id}.")
        return response

    except Exception as e:
        logging.error(f"Error in map_and_insert_dataset: {str(e)}")
        return {"error": str(e)}




def create_table_for_new_user(user_id):
    """
    Creates a new table for a user if it does not already exist.
    """
    try:
        # Connect to the database
        conn = psycopg2.connect(PSQL_URL)
        cur = conn.cursor()

        # SQL query to create a table dynamically
        create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS dataset_{str(user_id)} (
                id SERIAL PRIMARY KEY
            );
        """

        cur.execute(create_table_sql)
        conn.commit()
        cur.close()
        conn.close()

        print(f"✅ Table 'dataset_{user_id}' checked/created successfully.")
        return "ok"

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Error creating table: {str(e)}")


def add_column_if_not_exists(user_id, column_name, data_type="TEXT"):
    """
    Adds a missing column to the user's dataset table if it does not exist.
    """
    try:
        conn = psycopg2.connect(PSQL_URL)
        cur = conn.cursor()

        # Check if column exists
        cur.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='dataset_{user_id}' AND column_name='{column_name}';
        """)
        exists = cur.fetchone()

        # If column doesn't exist, add it
        if not exists:
            alter_sql = f'ALTER TABLE dataset_{user_id} ADD COLUMN "{column_name}" {data_type};'
            cur.execute(alter_sql)
            conn.commit()
            print(f"✅ Column '{column_name}' added to dataset_{user_id}.")

        cur.close()
        conn.close()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Error adding column '{column_name}': {str(e)}")


import psycopg2
from fastapi import HTTPException

def add_data_to_user_dataset(user_id, user_dataset):
    """
    Inserts data into the user's dataset table dynamically.
    Handles a list of dictionaries (multiple rows).
    """
    try:
        # Ensure table exists
        create_table_for_new_user(user_id)

        # Ensure all columns exist before inserting
        # If user_dataset is a list, we check the keys from the first dictionary
        for key in user_dataset[0].keys():
            add_column_if_not_exists(user_id, key)

        # Insert data dynamically
        conn = psycopg2.connect(PSQL_URL)
        cur = conn.cursor()

        # Prepare columns (same for all rows)
        columns = ', '.join(f'"{key}"' for key in user_dataset[0].keys())
        # Prepare values as a list of tuples for bulk insert
        values = [tuple(row.values()) for row in user_dataset]

        # SQL for bulk insert
        placeholders = ', '.join('%s' for _ in user_dataset[0].values())
        sql = f'INSERT INTO dataset_{user_id} ({columns}) VALUES ({placeholders});'

        # Execute the bulk insert
        cur.executemany(sql, values)
        conn.commit()
        cur.close()
        conn.close()

        print(f"✅ Data inserted into dataset_{user_id} successfully.")
        return {"status": "success", "message": "Data inserted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Error inserting data: {str(e)}")

