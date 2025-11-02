import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from models.item import Item, ItemCreate
from db.factory import create_db
import botocore.exceptions

app = FastAPI(title="Items API (DynamoDB PK compuesta)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET","POST","PUT","DELETE","OPTIONS"],
    allow_headers=["*"]
)

db = create_db()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/items", status_code=201, response_model=Item)
def create_item(payload: ItemCreate):
    try:
        created = db.create_item(payload)
        return created
    except botocore.exceptions.ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/items", response_model=List[Item])
def list_items():
    try:
        return db.get_all_items()
    except botocore.exceptions.ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/items/{item_id}", response_model=List[Item])
def get_items_by_id(item_id: str):
    """
    Devuelve 0..N items con la misma partition key 'id'.
    Si necesitas obtener un item concreto (id + categoria) usa query param ?categoria=X
    """
    try:
        items = db.query_by_id(item_id)
        return items
    except botocore.exceptions.ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/items/{item_id}/exact", response_model=Item)
def get_item_exact(item_id: str, categoria: str = Query(..., description="categoria (range key)")):
    try:
        it = db.get_item_exact(item_id, categoria)
        if not it:
            raise HTTPException(status_code=404, detail="Item no encontrado")
        return it
    except botocore.exceptions.ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: str, payload: ItemCreate, categoria: Optional[str] = Query(None, description="Categoria del item a actualizar. Si no se pasa y hay exactamente 1 item con ese id se usará esa.")):
    try:
        if categoria:
            target_cat = categoria
        else:
            # si no se pasa categoria, intentamos resolver: si hay 1 item lo usamos, si hay >1 devolvemos 400
            matches = db.query_by_id(item_id)
            if len(matches) == 0:
                raise HTTPException(status_code=404, detail="Item no encontrado")
            if len(matches) > 1:
                raise HTTPException(status_code=400, detail="Ambigüedad: hay varios items con ese id. Proporciona ?categoria=...")
            target_cat = matches[0].categoria

        updated = db.update_item(item_id, target_cat, payload)
        if not updated:
            raise HTTPException(status_code=404, detail="Item no encontrado para actualizar")
        return updated
    except botocore.exceptions.ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: str, categoria: Optional[str] = Query(None, description="Categoria del item a eliminar. Si no se pasa y hay exactamente 1 item con ese id se usará esa.")):
    try:
        if categoria:
            target_cat = categoria
        else:
            matches = db.query_by_id(item_id)
            if len(matches) == 0:
                raise HTTPException(status_code=404, detail="Item no encontrado")
            if len(matches) > 1:
                raise HTTPException(status_code=400, detail="Ambigüedad: hay varios items con ese id. Proporciona ?categoria=...")
            target_cat = matches[0].categoria
        deleted = db.delete_item(item_id, target_cat)
        if not deleted:
            raise HTTPException(status_code=404, detail="Item no encontrado para eliminar")
        return None
    except botocore.exceptions.ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))
