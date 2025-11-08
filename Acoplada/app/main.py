from flask import Flask, jsonify, request
from flask_cors import CORS
from db.factory import create_db
from models.item import ItemCreate
from pydantic import ValidationError
import botocore.exceptions

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

db = create_db()

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

# Crear un nuevo ítem
@app.route("/items", methods=["POST"])
def create_item():
    try:
        data = request.get_json() or {}

        # Validación ID
        if "id" not in data or not str(data["id"]).strip():
            return jsonify({"error":"ID vacío, debe ser un string válido"}), 400
        data["id"] = str(data["id"]).strip()

        # Validar cantidad si existe
        if "cantidad" in data:
            try:
                data["cantidad"] = int(data["cantidad"])
            except ValueError:
                return jsonify({"error":"Cantidad debe ser un número"}), 400

        payload = ItemCreate(**data)
        created = db.create_item(payload)
        return jsonify(created.dict()), 201

    except ValidationError as e:
        return jsonify({"error": "invalid payload", "details": e.errors()}), 400
    except botocore.exceptions.ClientError as e:
        return jsonify({"error": str(e)}), 500

# Listar todos los ítems
@app.route("/items", methods=["GET"])
def list_items():
    try:
        items = db.get_all_items()
        return jsonify([it.dict() for it in items]), 200
    except botocore.exceptions.ClientError as e:
        return jsonify({"error": str(e)}), 500

# Obtener un ítem por ID
@app.route("/items/<item_id>", methods=["GET"])
def get_item(item_id):
    try:
        item_id = str(item_id).strip()
        if not item_id:
            return jsonify({"error":"ID vacío, debe ser un string válido"}), 400

        it = db.get_item(item_id)
        if not it:
            return jsonify({"error": "Item no encontrado"}), 404
        return jsonify(it.dict()), 200
    except botocore.exceptions.ClientError as e:
        return jsonify({"error": str(e)}), 500

# Actualizar un ítem por ID
@app.route("/items/<item_id>", methods=["PUT"])
def update_item(item_id):
    try:
        item_id = str(item_id).strip()
        if not item_id:
            return jsonify({"error":"ID vacío, debe ser un string válido"}), 400

        data = request.get_json() or {}

        # Validar cantidad si existe
        if "cantidad" in data:
            try:
                data["cantidad"] = int(data["cantidad"])
            except ValueError:
                return jsonify({"error":"Cantidad debe ser un número"}), 400

        data["id"] = item_id
        payload = ItemCreate(**data)
        updated = db.update_item(item_id, payload)
        if not updated:
            return jsonify({"error": "Item no encontrado"}), 404
        return jsonify(updated.dict()), 200

    except ValidationError as e:
        return jsonify({"error": "invalid payload", "details": e.errors()}), 400
    except botocore.exceptions.ClientError as e:
        return jsonify({"error": str(e)}), 500

# Eliminar un ítem por ID
@app.route("/items/<item_id>", methods=["DELETE"])
def delete_item(item_id):
    try:
        item_id = str(item_id).strip()
        if not item_id:
            return jsonify({"error":"ID vacío, debe ser un string válido"}), 400

        deleted = db.delete_item(item_id)
        if not deleted:
            return jsonify({"error": "Item no encontrado"}), 404
        return "", 204

    except botocore.exceptions.ClientError as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
