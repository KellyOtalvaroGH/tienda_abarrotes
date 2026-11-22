from app.database import engine, Base
import app.models  # registra todas las tablas

Base.metadata.create_all(engine)
print("Tablas creadas")