import json
import botocore.exceptions
from Desacoplada.app.db.factory import create_db

db = create_db()

def handler(event, context):
    try:
        # Obtener todos los ítems de la tabla DynamoDB
        items = db.get_all_items()

        # Convertir cada ítem a un diccionario JSON serializable
        items_list = [it.model_dump() for it in items]

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,GET"
            },
            "body": json.dumps(items_list)
        }

    except botocore.exceptions.ClientError as e:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)})
        }