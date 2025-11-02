import os
from .dynamo_db import DynamoDBTable

def create_db():
    table_name = os.environ.get('TABLE_NAME') or os.environ.get('DYNAMO_TABLE') or "MiTablaEjemplo"
    region = os.environ.get('AWS_REGION')
    return DynamoDBTable(table_name=table_name, region_name=region)
