from typing import Optional, List
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
        """Crea un item. Usa el id que venga en payload; no genera UUID extra."""
        data = payload.model_dump()
        item = Item(**data)
        self.table.put_item(Item=item.model_dump())
        return item

    def get_item(self, item_id: str) -> Optional[Item]:
        try:
            resp = self.table.get_item(Key={'id': item_id})
            it = resp.get('Item')
            if it:
                return Item(**it)
            return None
        except ClientError as e:
            raise

    def get_all_items(self) -> List[Item]:
        resp = self.table.scan()
        return [Item(**it) for it in resp.get('Items', [])]

    def update_item(self, item_id: str, payload: ItemCreate) -> Optional[Item]:
        updatables = payload.model_dump(exclude={'id'})
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
