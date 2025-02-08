from ..supabase_client import supabase
from fastapi import HTTPException
import psycopg2

# Database connection string
PSQL_URL = "postgresql://postgres:hamzathegreat1234@db.gtizhtnrlztkccysrtkg.supabase.co:5432/postgres"


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


def add_data_to_user_dataset(user_id, user_dataset):
    """
    Inserts data into the user's dataset table dynamically.
    """
    try:
        # Ensure table exists
        create_table_for_new_user(user_id)

        # Ensure all columns exist before inserting
        for key in user_dataset.keys():
            add_column_if_not_exists(user_id, key)

        # Insert data dynamically
        conn = psycopg2.connect(PSQL_URL)
        cur = conn.cursor()

        columns = ', '.join(f'"{key}"' for key in user_dataset.keys())
        values = ', '.join('%s' for _ in user_dataset.values())
        sql = f'INSERT INTO dataset_{user_id} ({columns}) VALUES ({values});'

        cur.execute(sql, list(user_dataset.values()))
        conn.commit()
        cur.close()
        conn.close()

        print(f"✅ Data inserted into dataset_{user_id} successfully.")
        return {"status": "success", "message": "Data inserted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Error inserting data: {str(e)}")
