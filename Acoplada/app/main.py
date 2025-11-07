from flask import Flask, jsonify, request
from flask_cors import CORS
from db.factory import create_db
from models.item import Item, ItemCreate
import botocore.exceptions

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

db = create_db()

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/items", methods=["POST"])
def create_item():
    try:
        data = request.get_json()
        payload = ItemCreate(**data)
        created = db.create_item(payload)
        return jsonify(created.dict()), 201
    except botocore.exceptions.ClientError as e:
        return jsonify({"error": str(e)}), 500

@app.route("/items", methods=["GET"])
def list_items():
    try:
        items = db.get_all_items()
        return jsonify([it.dict() for it in items]), 200
    except botocore.exceptions.ClientError as e:
        return jsonify({"error": str(e)}), 500

@app.route("/items/<item_id>", methods=["GET"])
def get_items_by_id(item_id):
    try:
        items = db.query_by_id(item_id)
        return jsonify([it.dict() for it in items]), 200
    except botocore.exceptions.ClientError as e:
        return jsonify({"error": str(e)}), 500

@app.route("/items/<item_id>/exact", methods=["GET"])
def get_item_exact(item_id):
    categoria = request.args.get("categoria")
    if not categoria:
        return jsonify({"error": "categoria es requerida"}), 400
    try:
        it = db.get_item_exact(item_id, categoria)
        if not it:
            return jsonify({"error": "Item no encontrado"}), 404
        return jsonify(it.dict()), 200
    except botocore.exceptions.ClientError as e:
        return jsonify({"error": str(e)}), 500

@app.route("/items/<item_id>", methods=["PUT"])
def update_item(item_id):
    data = request.get_json()
    categoria = request.args.get("categoria")
    try:
        payload = ItemCreate(**data)
        updated = db.update_item(item_id, categoria, payload)
        if not updated:
            return jsonify({"error": "Item no encontrado"}), 404
        return jsonify(updated.dict()), 200
    except botocore.exceptions.ClientError as e:
        return jsonify({"error": str(e)}), 500

@app.route("/items/<item_id>", methods=["DELETE"])
def delete_item(item_id):
    categoria = request.args.get("categoria")
    try:
        deleted = db.delete_item(item_id, categoria)
        if not deleted:
            return jsonify({"error": "Item no encontrado"}), 404
        return "", 204
    except botocore.exceptions.ClientError as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
