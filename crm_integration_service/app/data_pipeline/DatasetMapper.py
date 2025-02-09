import pandas as pd
import json
from ..utils.groq_chat import GroqChat


class DatasetMapper:
    def __init__(self, model_name="llama-3.3-70b-versatile", rules_path="./utils/mapping_rules.json"):
        self.llm = GroqChat(model_name)
        self.rules_path = rules_path
        self.rules = self.load_mapping_rules()
        self.dataset:pd.DataFrame

    def load_mapping_rules(self):
        """Load column mapping rules from a JSON file."""
        try:
            with open(self.rules_path, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading mapping rules: {e}")
            return {}
        
    def describe_dataset(self, df_head: pd.DataFrame):
        print("dataset")
        """Generate a JSON description of each column in a dataset."""
        system_prompt = """You are a data analysis expert. When given a pandas DataFrame's head output, carefully analyze each column and provide a comprehensive yet concise description. Your response must be a valid JSON object where:
        - Keys are column names
        - Values are detailed descriptions capturing the column's nature, potential meaning, and data characteristics
        - Descriptions should be precise, informative, and max 100 characters long"""

        user_prompt = f"""Analyze the following DataFrame head and provide a JSON description of each column's characteristics and potential meaning:
        {df_head.to_string()}
        Format your response as a valid JSON object with descriptive insights for each column."""
        try:
            response = self.llm.simple_chat(system_prompt=system_prompt, user_prompt=user_prompt, temperature=0.95, max_tokens=2000)
            return response
        except Exception as e:
            print(f"Error in describe_dataset: {e}")
            return {}
    
    def check_column_compatibility(self, column_name: str, column_desc: str, dataset: dict):
        """Check if a column from one dataset matches another based on descriptions."""
        system_prompt = """You are an expert in checking compatibility for mapping COLUMNS across different datasets. Your task is to determine the best match for a target column from the source dataset based on their descriptions. 
        You will be given the target column and its description along with multiple source columns and their descriptions.

        Your response should follow these rules:
        - Compare the **target column's description** with the **descriptions of all source columns**.
        - If the descriptions of the source columns align with the target column, return the **name of the source column** that best matches the target column.
        - If no source column is a good match for the target column, return "Nothing Compatible".
        - You can choose multiple features if and only if they fit.
        - Do not output anything other than the column names.
        - If there is more than one column, separate them with a comma (',')."""

        user_prompt = f"""The target column and its description are as follows:
        Target Column: {column_name}
        Description: {column_desc}

        Here are the source columns with their descriptions:
        {json.dumps(dataset)}

        Your output should only be the column name(s) or "Nothing Compatible"."""

        try:
            response = self.llm.simple_chat(user_prompt=user_prompt, system_prompt=system_prompt, max_tokens=1000)
            return response.strip()
        except Exception as e:
            print(f"Error in check_column_compatibility: {e}")
            return "Nothing Compatible"
    
    def get_mapping_values(self, report):
        """Get the best column mappings based on rules."""
        mappings = []
        try:
            for key, value in self.rules.get("mapping_rules", {}).items():
                mappings.append(self.check_column_compatibility(column_name=key, column_desc=value, dataset=report))
        except Exception as e:
            print(f"Error in get_mapping_values: {e}")
        return mappings
    
    def map_dataset(self,json_data:list, source_path: str=None):
        """Map columns from a source dataset to a target dataset based on predefined rules."""
        try:
            # df = pd.read_csv(source_path)
            df=pd.DataFrame(json_data)
            print(df)

            report = self.describe_dataset(df_head=df.head())
            mappings = self.get_mapping_values(report)
            new_dataset = pd.DataFrame()
            not_compatible = []
            
            keys = list(self.rules.get("mapping_rules", {}).keys())
            print(keys)

            for i, source in enumerate(mappings):
                if source == "Nothing Compatible":
                    not_compatible.append(keys[i])
                elif "," in source:
                    new_dataset[keys[i]] = df[[col.strip() for col in source.split(",")]].agg(lambda x: ' '.join(x.dropna().astype(str)), axis=1)
                else:
                    new_dataset[keys[i]] = df[source.strip()]
            
            self.dataset=new_dataset
            return new_dataset, not_compatible
        except Exception as e:
            print(f"Error in map_dataset: {e}")
            return pd.DataFrame(), []
        
    def store_dataset(self,path="./utils/stored_dataset.csv"):
        self.dataset.to_csv(path)
    
        
