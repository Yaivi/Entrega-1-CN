import json
import botocore.exceptions
from Desacoplada.app.db.factory import create_db


# Inicializamos DynamoDB una vez por Lambda
db = create_db()

def handler(event, context):
    try:
        # Obtener el parámetro "item_id" del path
        item_id = event.get("pathParameters", {}).get("item_id")

        if not item_id:
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Falta el parámetro item_id"})
            }

        # Eliminar el item de DynamoDB
        deleted = db.delete_item(item_id)

        # Si no existe el item
        if not deleted:
            return {
                "statusCode": 404,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Item no encontrado"})
            }

        # Eliminado correctamente → 204 No Content
        return {
            "statusCode": 204,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,DELETE"
            },
            "body": ""
        }

    except botocore.exceptions.ClientError as e:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)})
        }
