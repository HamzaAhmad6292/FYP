

import requests

url = "http://localhost:8000/api/v1/analyze"
files = {"file": open("New-SuperStore_Sales_Dataset.csv", "rb")}

response = requests.post(url, files=files)
data = response.json()

print("Columns returned:", data["raw_data"]["columns"])
print("First 3 rows:", data["raw_data"]["values"][:3])