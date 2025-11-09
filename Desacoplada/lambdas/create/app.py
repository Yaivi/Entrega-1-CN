import json
from pydantic import ValidationError
import botocore.exceptions
from Desacoplada.app.db.factory import create_db
from Desacoplada.app.models.item import ItemCreate

db = create_db()

def handler(event, context):
    try:
        data = json.loads(event.get('body', '{}'))
        payload = ItemCreate(**data)

        # Crear item en la tabla DynamoDB
        item = db.create_item(payload)

        # Devolver respuesta HTTP
        return {
            "statusCode": 201,
            "headers": {
                "Access-Control-Allow-Origin": "*",  # CORS
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps(item.model_dump())
        }

    except ValidationError as e:
        return {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": e.errors()})
        }

    except botocore.exceptions.ClientError as e:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)})
        }
