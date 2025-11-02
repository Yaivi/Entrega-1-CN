from flask import Flask, request, jsonify
import boto3
import os

app = Flask(__name__)

# Conexión a DynamoDB usando el rol IAM de ECS
dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'us-east-1'))
table = dynamodb.Table(os.getenv('DYNAMO_TABLE', 'MiTablaEjemplo'))

REQUIRED_FIELDS = ['nombre', 'fecha', 'cantidad']

# Create
@app.route('/items', methods=['POST'])
def create_item():
    data = request.json
    for field in REQUIRED_FIELDS + ['id', 'categoria']:
        if field not in data:
            return jsonify({'error': f'Falta el campo {field}'}), 400
    table.put_item(Item=data)
    return jsonify({'message': 'Item creado'}), 201

# Read all
@app.route('/items', methods=['GET'])
def get_items():
    resp = table.scan()
    return jsonify(resp.get('Items', [])), 200

# Read by ID
@app.route('/items/<id>', methods=['GET'])
def get_item(id):
    categoria = request.args.get('categoria', 'default')  # ejemplo si RANGE key es categoria
    resp = table.get_item(Key={'id': id, 'categoria': categoria})
    item = resp.get('Item')
    if not item:
        return jsonify({'error': 'Item no encontrado'}), 404
    return jsonify(item), 200

# Update
@app.route('/items/<id>', methods=['PUT'])
def update_item(id):
    categoria = request.args.get('categoria', 'default')
    data = request.json
    update_expr = "SET " + ", ".join(f"{k}=:{k}" for k in data.keys())
    expr_values = {f":{k}": v for k, v in data.items()}
    table.update_item(
        Key={'id': id, 'categoria': categoria},
        UpdateExpression=update_expr,
        ExpressionAttributeValues=expr_values
    )
    return jsonify({'message': 'Item actualizado'}), 200

# Delete
@app.route('/items/<id>', methods=['DELETE'])
def delete_item(id):
    categoria = request.args.get('categoria', 'default')
    table.delete_item(Key={'id': id, 'categoria': categoria})
    return jsonify({'message': 'Item eliminado'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 80)))
