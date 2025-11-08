from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, timezone
import uuid

class ItemCreate(BaseModel):
    nombre: str = Field(..., min_length=1)
    fecha: Optional[str] = None  # se genera si no se da
    cantidad: int = Field(..., ge=0)

    @field_validator('fecha', mode='before')
    def normalize_fecha(cls, v):
        # Genera fecha actual UTC con timezone-aware si no se da
        return v or datetime.now(timezone.utc).isoformat()

class Item(ItemCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "nombre": "Camiseta roja",
                "fecha": "2025-11-03T12:34:56+00:00",
                "cantidad": 10
            }
        }
