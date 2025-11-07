import os
from typing import Optional, List, Dict, Any
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from models.item import Item, ItemCreate

class DynamoDBTable:
    def __init__(self, table_name: str, region_name: Optional[str] = None):
        session = boto3.session.Session()
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        self.table = self.dynamodb.Table('MiTablaEjemplo')

    def create_item(self, payload: ItemCreate, item_id: Optional[str] = None) -> Item:
        data = payload.dict()
        if not item_id:
            # Genera id usando el modelo Item para mantener la lógica centralizada
            tmp = Item(id=None, **data)
            item = tmp
        else:
            item = Item(id=item_id, **data)
        self.table.put_item(Item=item.dict())
        return item

    def query_by_id(self, item_id: str) -> List[Item]:
        """Query por partition key 'id' — devuelve lista (puede haber varias categorias)."""
        resp = self.table.query(
            KeyConditionExpression=Key('id').eq(item_id)
        )
        items = [Item(**it) for it in resp.get('Items', [])]
        return items

    def get_item_exact(self, item_id: str, categoria: str) -> Optional[Item]:
        """GetItem con clave completa (id + categoria)."""
        resp = self.table.get_item(Key={'id': item_id, 'categoria': categoria})
        it = resp.get('Item')
        if it:
            return Item(**it)
        return None

    def get_all_items(self) -> List[Item]:
        """Scan completo — OK para pruebas/small data. Añadir paginación si hace falta."""
        resp = self.table.scan()
        items = [Item(**it) for it in resp.get('Items', [])]
        return items

    def update_item(self, item_id: str, categoria: str, payload: ItemCreate) -> Optional[Item]:
        # Construimos UpdateExpression excepto sobre PKs (id, categoria)
        updatables: Dict[str, Any] = payload.dict()
        expr_parts = []
        expr_vals = {}
        for k, v in updatables.items():
            if k in ('categoria',):  # categoría forma parte de la PK: no la actualizamos
                continue
            expr_parts.append(f"{k} = :{k}")
            expr_vals[f":{k}"] = v
        if not expr_parts:
            # nothing to update
            return self.get_item_exact(item_id, categoria)
        update_expr = "SET " + ", ".join(expr_parts)
        try:
            resp = self.table.update_item(
                Key={'id': item_id, 'categoria': categoria},
                UpdateExpression=update_expr,
                ExpressionAttributeValues=expr_vals,
                ReturnValues="ALL_NEW",
                ConditionExpression="attribute_exists(id) AND attribute_exists(categoria)"
            )
            return Item(**resp['Attributes'])
        except ClientError as e:
            code = e.response['Error'].get('Code', '')
            if code == 'ConditionalCheckFailedException':
                return None
            raise

    def delete_item(self, item_id: str, categoria: str) -> bool:
        try:
            self.table.delete_item(
                Key={'id': item_id, 'categoria': categoria},
                ConditionExpression="attribute_exists(id) AND attribute_exists(categoria)"
            )
            return True
        except ClientError as e:
            code = e.response['Error'].get('Code', '')
            if code == 'ConditionalCheckFailedException':
                return False
            raise
