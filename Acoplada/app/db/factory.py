import os
from .dynamo_db import DynamoDBTable

def create_db():
    
    return DynamoDBTable(table_name="MiTablaEjemplo", region_name="us-east-1")