import os
import pandas as pd
import requests
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

OPENMETADATA_HOST = os.getenv("OPENMETADATA_HOST")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
EXCEL_FILE_PATH = os.getenv("EXCEL_FILE_PATH", "metadata.xlsx")

HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json",
}


def create_service(service_name: str, description: str):
    url = f"{OPENMETADATA_HOST}/v1/services/databaseServices"
    data = {
        "name": service_name,
        "serviceType": "CustomDatabase",
        "description": description
    }
    res = requests.post(url, json=data, headers=HEADERS)
    return res.json()


def get_or_create_database(service_id, db_name: str, description: str):
    url = f"{OPENMETADATA_HOST}/v1/databases"
    data = {
        "name": db_name,
        "description": description,
        "service": {"id": service_id, "type": "databaseService"}
    }
    res = requests.post(url, json=data, headers=HEADERS)
    return res.json()


def get_or_create_schema(db_id, schema_name: str, schema_description: str):
    url = f"{OPENMETADATA_HOST}/v1/databaseSchemas"
    data = {
        "name": schema_name,
        "description": schema_description,
        "database": {"id": db_id, "type": "database"}
    }
    res = requests.post(url, json=data, headers=HEADERS)
    return res.json()


def get_or_create_table(schema_id, table_name: str, table_description: str, columns: list):
    url = f"{OPENMETADATA_HOST}/v1/tables"
    data = {
        "name": table_name,
        "description": table_description,
        "columns": columns,
        "databaseSchema": {"id": schema_id, "type": "databaseSchema"}
    }
    res = requests.post(url, json=data, headers=HEADERS)
    return res.json()


def build_column(name, dtype, desc):
    return {
        "name": name,
        "dataType": dtype.upper(),
        "description": desc
    }


df = pd.read_excel(EXCEL_FILE_PATH).fillna("")

for _, row in df.iterrows():
    service = create_service(row['service_name'], row['Service_description'])
    service_id = service['id']

    database = get_or_create_database(service_id, row['database_name'], row['Database_descriptiion'])
    db_id = database['id']

    schema = get_or_create_schema(db_id, row['schema_name'], row['schecma_description'])
    schema_id = schema['id']

    column = build_column(row['column_na,e'], row['Column_type'], row['Column_description'])

    table = get_or_create_table(schema_id, row['table_name'], row['table_description'], [column])

    print(f"✅ Table created: {table['name']}")
