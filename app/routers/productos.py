
from fastapi import APIRouter, HTTPException, status

from app.database import obtener_conexion
from app.schemas import ProductoCrear, ProductoRespuesta

router = APIRouter(
    prefix="/productos",
    tags=["Productos"]
)


@router.post("/", response_model=ProductoRespuesta, status_code=status.HTTP_201_CREATED)
def crear_producto(producto: ProductoCrear):
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO productos (nombre, precio, stock)
                VALUES (%s, %s, %s)
                """,
                (producto.nombre, producto.precio, producto.stock)
            )

            producto_id = cursor.lastrowid

        conexion.commit()

        return {
            "id": producto_id,
            "nombre": producto.nombre,
            "precio": producto.precio,
            "stock": producto.stock
        }

    except Exception:
        conexion.rollback()
        raise HTTPException(
            status_code=500,
            detail="No se pudo crear el producto"
        )

    finally:
        conexion.close()


@router.get("/", response_model=list[ProductoRespuesta])
def listar_productos():
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, nombre, precio, stock
                FROM productos
                ORDER BY id
                """
            )
            return cursor.fetchall()

    finally:
        conexion.close()


@router.get("/{producto_id}", response_model=ProductoRespuesta)
def consultar_producto(producto_id: int):
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, nombre, precio, stock
                FROM productos
                WHERE id = %s
                """,
                (producto_id,)
            )
            producto = cursor.fetchone()

        if not producto:
            raise HTTPException(
                status_code=404,
                detail="Producto no encontrado"
            )

        return producto

    finally:
        conexion.close()


@router.put("/{producto_id}", response_model=ProductoRespuesta)
def actualizar_producto(producto_id: int, datos: ProductoCrear):
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM productos WHERE id = %s",
                (producto_id,)
            )

            if not cursor.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail="Producto no encontrado"
                )

            cursor.execute(
                """
                UPDATE productos
                SET nombre = %s, precio = %s, stock = %s
                WHERE id = %s
                """,
                (
                    datos.nombre,
                    datos.precio,
                    datos.stock,
                    producto_id
                )
            )

        conexion.commit()

        return {
            "id": producto_id,
            "nombre": datos.nombre,
            "precio": datos.precio,
            "stock": datos.stock
        }

    except HTTPException:
        conexion.rollback()
        raise

    except Exception:
        conexion.rollback()
        raise HTTPException(
            status_code=500,
            detail="No se pudo actualizar el producto"
        )

    finally:
        conexion.close()


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(producto_id: int):
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                "DELETE FROM productos WHERE id = %s",
                (producto_id,)
            )

            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Producto no encontrado"
                )

        conexion.commit()

    except HTTPException:
        conexion.rollback()
        raise

    except Exception as error:
        conexion.rollback()

        if "foreign key constraint fails" in str(error).lower():
            raise HTTPException(
                status_code=409,
                detail="No se puede eliminar el producto porque aparece en pedidos"
            )

        raise HTTPException(
            status_code=500,
            detail="No se pudo eliminar el producto"
        )

    finally:
        conexion.close()
