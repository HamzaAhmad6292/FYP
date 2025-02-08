import pandas as pd

def detect_schema(file_path, file_type='csv', sheet_name=0, db_query=None, db_connection=None):
    """
    Detect schema from a data file or database query.
    
    Args:
        file_path (str): Path to the file (CSV, Excel, etc.).
        file_type (str): Type of file ('csv' or 'excel').
        sheet_name (int/str): Sheet name or index (only for Excel files).
        db_query (str, optional): SQL query if extracting from a database.
        db_connection (SQLAlchemy connection, optional): Database connection object.
    
    Returns:
        dict: Schema details with column names, data types, and sample values.
    """
    
    if db_query and db_connection:
        df = pd.read_sql(db_query, db_connection)
    elif file_type == 'csv':
        df = pd.read_csv(file_path, nrows=100)
    elif file_type == 'excel':
        df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=100)
    else:
        raise ValueError("Unsupported file type or missing database parameters")
    
    schema = {}
    for col in df.columns:
        schema[col] = {
            'Data Type': str(df[col].dtype),
            'Sample Values': df[col].dropna().unique()[:5].tolist()
        }
    
    return schema


