
from fastapi import FastAPI

from app.routers import clientes

app = FastAPI(
    title="Tienda ADSO API",
    description="API REST para gestionar clientes, productos y pedidos",
    version="1.0.0"
)

app.include_router(clientes.router)


@app.get("/")
def inicio():
    return {
        "mensaje": "Bienvenido a Tienda ADSO API",
        "estado": "funcionando"
    }


@app.get("/salud")
def verificar_salud():
    return {
        "estado": "correcto",
        "mensaje": "La API esta funcionando"
    }
