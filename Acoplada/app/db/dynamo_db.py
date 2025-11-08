import os
from typing import Optional, List, Dict, Any
from uuid import uuid4
import boto3
from botocore.exceptions import ClientError
from models.item import Item, ItemCreate


class DynamoDBTable:
    def __init__(self, table_name: str, region_name: Optional[str] = None):
        """Inicializa la tabla DynamoDB con nombre y región opcional."""
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name or 'us-east-1')
        self.table = self.dynamodb.Table(table_name)

    def create_item(self, payload: ItemCreate) -> Item:
        """Crea un item. Si no se pasa id, genera uno automáticamente."""
        data = payload.dict()
        if not data.get('id'):
            data['id'] = str(uuid4())
        item = Item(**data)
        self.table.put_item(Item=item.dict())
        return item

    def get_item(self, item_id: str) -> Optional[Item]:
        """Obtiene un item por id."""
        try:
            resp = self.table.get_item(Key={'id': item_id})
            it = resp.get('Item')
            if it:
                return Item(**it)
            return None
        except ClientError as e:
            raise

    def get_all_items(self) -> List[Item]:
        """Obtiene todos los items (scan completo, cuidado con tablas grandes)."""
        resp = self.table.scan()
        items = [Item(**it) for it in resp.get('Items', [])]
        return items

    def update_item(self, item_id: str, payload: ItemCreate) -> Optional[Item]:
        """Actualiza un item por id. No se puede cambiar el id."""
        updatables = payload.dict(exclude={'id'})
        if not updatables:
            return self.get_item(item_id)

        expr_parts = []
        expr_vals = {}
        for k, v in updatables.items():
            expr_parts.append(f"{k} = :{k}")
            expr_vals[f":{k}"] = v

        update_expr = "SET " + ", ".join(expr_parts)

        try:
            resp = self.table.update_item(
                Key={'id': item_id},
                UpdateExpression=update_expr,
                ExpressionAttributeValues=expr_vals,
                ReturnValues="ALL_NEW",
                ConditionExpression="attribute_exists(id)"
            )
            return Item(**resp['Attributes'])
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return None
            raise

    def delete_item(self, item_id: str) -> bool:
        """Elimina un item por id."""
        try:
            self.table.delete_item(
                Key={'id': item_id},
                ConditionExpression="attribute_exists(id)"
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return False
            raise
