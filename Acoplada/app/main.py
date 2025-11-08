from flask import Flask, jsonify, request
from flask_cors import CORS
from db.factory import create_db
from models.item import ItemCreate
from pydantic import ValidationError
import botocore.exceptions

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

db = create_db()  # DynamoDBTable

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

# Crear un item
@app.route("/items", methods=["POST"])
def create_item():
    try:
        data = request.get_json() or {}
        payload = ItemCreate(**data)
        item = db.create_item(payload)
        return jsonify(item.model_dump()), 201
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    except botocore.exceptions.ClientError as e:
        return jsonify({"error": str(e)}), 500

# Listar todos los items
@app.route("/items", methods=["GET"])
def list_items():
    try:
        items = db.get_all_items()
        return jsonify([it.model_dump() for it in items]), 200
    except botocore.exceptions.ClientError as e:
        return jsonify({"error": str(e)}), 500

# Obtener item por ID
@app.route("/items/<item_id>", methods=["GET"])
def get_item(item_id):
    try:
        it = db.get_item(item_id)
        if not it:
            return jsonify({"error": "Item no encontrado"}), 404
        return jsonify(it.model_dump()), 200
    except botocore.exceptions.ClientError as e:
        return jsonify({"error": str(e)}), 500

# Actualizar item
@app.route("/items/<item_id>", methods=["PUT"])
def update_item(item_id):
    try:
        data = request.get_json() or {}
        data["id"] = item_id
        payload = ItemCreate(**data)
        updated = db.update_item(item_id, payload)
        if not updated:
            return jsonify({"error": "Item no encontrado"}), 404
        return jsonify(updated.model_dump()), 200
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    except botocore.exceptions.ClientError as e:
        return jsonify({"error": str(e)}), 500

# Eliminar item
@app.route("/items/<item_id>", methods=["DELETE"])
def delete_item(item_id):
    try:
        deleted = db.delete_item(item_id)
        if not deleted:
            return jsonify({"error": "Item no encontrado"}), 404
        return "", 204
    except botocore.exceptions.ClientError as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
