from ..supabase_client import supabase
from fastapi import HTTPException
import psycopg2


def create_table_for_newUser(user_id,user_dataset):
    try:
        DB_URL = "postgresql://postgres.gtizhtnrlztkccysrtkg:H@mzaahmad1234@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"

# Connect to the database
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        # SQL query to create a table for the new user
        create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS "dataset_{str(user_id)}" (
                id INTEGER
            );
        """
        


        # Execute the SQL query
        # response = supabase.table(f"dataset_{str(user_id)}").insert(user_dataset).execute()
        # print(response)
        cur.execute(create_table_sql)
        conn.commit()

        cur.close()
        conn.close()

        # Check if the response contains an error
        # if response.status_code != 200:
        #     raise HTTPException(status_code=response.status_code, detail=f"Error creating table: {response.data}")

        return {"ok":"ok"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while creating the table: {str(e)}")


def add_data_to_userDataset(user_data):
    try:
        # Insert the dataset into the user's table
        response = supabase.table(f"dataset_{user_data.user_id}").insert(user_data.user_dataset).execute()

        # Check if the response contains an error
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Error inserting data: {response.data}")

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while adding data to the dataset: {str(e)}")
