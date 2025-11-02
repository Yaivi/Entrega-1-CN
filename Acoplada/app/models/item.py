from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import uuid

class ItemCreate(BaseModel):
    # revisar que como mínimo tenga 3 atributos: name, category, value 
    categoria: str = Field(..., min_length=1)
    nombre: str = Field(..., min_length=1)
    fecha: Optional[str] = None  # string opcional, si no se da se generará
    cantidad: int = Field(..., ge=0)

    @validator('fecha', pre=True, always=True)
    def normalize_fecha(cls, v):
        if v is None:
            return datetime.utcnow().isoformat()
        return v

class Item(ItemCreate):
    # Campos internos / clave primaria
    id: str = Field(...)

    @validator('id', pre=True, always=True)
    def set_id(cls, v):
        return v or str(uuid.uuid4())
