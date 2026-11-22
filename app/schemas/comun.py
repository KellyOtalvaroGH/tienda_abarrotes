from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SalidaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    activo: bool
    fecha_creacion: datetime
    fecha_modificacion: datetime