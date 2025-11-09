import json
import botocore.exceptions
from Desacoplada.app.db.factory import create_db

db = create_db()

def handler(event, context):
    try:
        # Obtener el parámetro "item_id" desde el path de API Gateway
        item_id = event.get("pathParameters", {}).get("item_id")

        if not item_id:
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Falta el parámetro item_id"})
            }

        # Obtener el ítem de DynamoDB
        item = db.get_item(item_id)

        if not item:
            return {
                "statusCode": 404,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Item no encontrado"})
            }

        # Devolver el item encontrado
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,GET"
            },
            "body": json.dumps(item.model_dump())
        }

    except botocore.exceptions.ClientError as e:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)})
        }