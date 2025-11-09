import json
import botocore.exceptions
from pydantic import ValidationError
from Desacoplada.app.db.factory import create_db
from Desacoplada.app.models.item import ItemCreate

# Conexión persistente a DynamoDB
db = create_db()

def handler(event, context):
    try:
        # Extraer ID del path (API Gateway lo pasa en pathParameters)
        item_id = event["pathParameters"]["id"]

        # Obtener cuerpo del request
        data = json.loads(event.get("body") or "{}")

        # Forzar que el ID del path prevalezca
        data["id"] = item_id

        # Validar payload con Pydantic
        payload = ItemCreate(**data)

        # Actualizar en DynamoDB
        updated = db.update_item(item_id, payload)

        if not updated:
            return {
                "statusCode": 404,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Item no encontrado"})
            }

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,PUT"
            },
            "body": json.dumps(updated.model_dump())
        }

    except ValidationError as e:
        return {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "invalid payload", "details": e.errors()})
        }

    except botocore.exceptions.ClientError as e:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)})
        }
