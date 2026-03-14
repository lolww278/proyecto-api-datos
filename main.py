from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import mysql.connector
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde .env
load_dotenv()

app = FastAPI(title="API de Datos - Sistema de Salud")

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

security = HTTPBearer()


# ── Helpers de base de datos ──────────────────────────────────────────────────

def get_db_connection():
    """Crea una nueva conexión a la BD por cada request (evita caídas globales)."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306))
    )


# ── Dependencia de autenticación ──────────────────────────────────────────────

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependencia de FastAPI: valida el JWT en el header Authorization.
    Inyectar en cualquier endpoint para protegerlo.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=401, detail="Token inválido o expirado")


# ── Modelos Pydantic ──────────────────────────────────────────────────────────

class Usuario(BaseModel):
    email: str
    nombre_c: str
    rol: str
    genero: str


class Paciente(BaseModel):
    id_usuario: int
    nombre: str
    apellido: str
    fecha_nacimiento: str  # Formato YYYY-MM-DD
    genero: str            # 'Masculino', 'Femenino', 'Otro'
    numero_contacto: str
    direccion: str


class Profesional(BaseModel):
    id_usuario: int
    nombre: str
    apellido: str
    numero_licencia: str
    tipo_profesional: str  # 'psicologo' o 'psiquiatra'
    numero_contacto: str


# ── Endpoints: Usuarios ───────────────────────────────────────────────────────

@app.get("/usuarios")
def get_all_usuarios(token_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios")
        usuarios = cursor.fetchall()
        return {"resultado": jsonable_encoder(usuarios)}
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=500, detail=f"Error de base de datos: {err}")
    finally:
        cursor.close()
        conn.close()


@app.get("/usuarios/{id}")
def get_usuario_by_id(id: int, token_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
        usuario = cursor.fetchone()
        if not usuario:
            raise HTTPException(
                status_code=404, detail="Usuario no encontrado")
        return {"resultado": jsonable_encoder(usuario)}
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=500, detail=f"Error de base de datos: {err}")
    finally:
        cursor.close()
        conn.close()


@app.post("/usuarios", status_code=201)
def add_usuario(usuario: Usuario, token_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (email, nombre_c, rol, genero) VALUES (%s, %s, %s, %s)",
            (usuario.email, usuario.nombre_c, usuario.rol, usuario.genero)
        )
        conn.commit()
        return {"informacion": "Usuario registrado con éxito"}
    except mysql.connector.IntegrityError:
        raise HTTPException(status_code=409, detail="El email ya existe")
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=500, detail=f"Error de base de datos: {err}")
    finally:
        cursor.close()
        conn.close()


@app.put("/usuarios/{id}")
def update_usuario(id: int, usuario: Usuario, token_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuarios SET email=%s, nombre_c=%s, rol=%s, genero=%s WHERE id=%s",
            (usuario.email, usuario.nombre_c, usuario.rol, usuario.genero, id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404, detail="Usuario no encontrado")
        return {"informacion": "Usuario actualizado con éxito"}
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=500, detail=f"Error de base de datos: {err}")
    finally:
        cursor.close()
        conn.close()


@app.delete("/usuarios/{id}", status_code=200)
def delete_usuario(id: int, token_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404, detail="Usuario no encontrado")
        return {"informacion": "Usuario eliminado con éxito"}
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=500, detail=f"Error de base de datos: {err}")
    finally:
        cursor.close()
        conn.close()


# ── Endpoints: Pacientes ──────────────────────────────────────────────────────

@app.get("/pacientes")
def get_all_pacientes(token_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pacientes")
        pacientes = cursor.fetchall()
        return {"resultado": jsonable_encoder(pacientes)}
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=500, detail=f"Error de base de datos: {err}")
    finally:
        cursor.close()
        conn.close()


@app.get("/pacientes/{id}")
def get_paciente_by_id(id: int, token_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pacientes WHERE id = %s", (id,))
        paciente = cursor.fetchone()
        if not paciente:
            raise HTTPException(
                status_code=404, detail="Paciente no encontrado")
        return {"resultado": jsonable_encoder(paciente)}
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=500, detail=f"Error de base de datos: {err}")
    finally:
        cursor.close()
        conn.close()


@app.post("/pacientes", status_code=201)
def add_paciente(paciente: Paciente, token_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO pacientes (id_usuario, nombre, apellido, fecha_nacimiento, genero, numero_contacto, direccion)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (paciente.id_usuario, paciente.nombre, paciente.apellido,
             paciente.fecha_nacimiento, paciente.genero, paciente.numero_contacto, paciente.direccion)
        )
        conn.commit()
        return {"informacion": "Paciente registrado con éxito"}
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=500, detail=f"Error de base de datos: {err}")
    finally:
        cursor.close()
        conn.close()


@app.put("/pacientes/{id}")
def update_paciente(id: int, paciente: Paciente, token_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE pacientes
               SET id_usuario=%s, nombre=%s, apellido=%s, fecha_nacimiento=%s,
                   genero=%s, numero_contacto=%s, direccion=%s
               WHERE id=%s""",
            (paciente.id_usuario, paciente.nombre, paciente.apellido,
             paciente.fecha_nacimiento, paciente.genero, paciente.numero_contacto,
             paciente.direccion, id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404, detail="Paciente no encontrado")
        return {"informacion": "Paciente actualizado con éxito"}
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=500, detail=f"Error de base de datos: {err}")
    finally:
        cursor.close()
        conn.close()


@app.delete("/pacientes/{id}")
def delete_paciente(id: int, token_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pacientes WHERE id = %s", (id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404, detail="Paciente no encontrado")
        return {"informacion": "Paciente eliminado con éxito"}
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=500, detail=f"Error de base de datos: {err}")
    finally:
        cursor.close()
        conn.close()


# ── Endpoints: Profesionales ──────────────────────────────────────────────────

@app.get("/profesionales")
def get_all_profesionales(token_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM profesionales")
        profesionales = cursor.fetchall()
        return {"resultado": jsonable_encoder(profesionales)}
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=500, detail=f"Error de base de datos: {err}")
    finally:
        cursor.close()
        conn.close()


@app.get("/profesionales/{id}")
def get_profesional_by_id(id: int, token_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM profesionales WHERE id = %s", (id,))
        profesional = cursor.fetchone()
        if not profesional:
            raise HTTPException(
                status_code=404, detail="Profesional no encontrado")
        return {"resultado": jsonable_encoder(profesional)}
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=500, detail=f"Error de base de datos: {err}")
    finally:
        cursor.close()
        conn.close()


@app.post("/profesionales", status_code=201)
def add_profesional(profesional: Profesional, token_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO profesionales (id_usuario, nombre, apellido, numero_licencia, tipo_profesional, numero_contacto)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (profesional.id_usuario, profesional.nombre, profesional.apellido,
             profesional.numero_licencia, profesional.tipo_profesional, profesional.numero_contacto)
        )
        conn.commit()
        return {"informacion": "Profesional registrado con éxito"}
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=500, detail=f"Error de base de datos: {err}")
    finally:
        cursor.close()
        conn.close()


@app.put("/profesionales/{id}")
def update_profesional(id: int, profesional: Profesional, token_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE profesionales
               SET id_usuario=%s, nombre=%s, apellido=%s, numero_licencia=%s,
                   tipo_profesional=%s, numero_contacto=%s
               WHERE id=%s""",
            (profesional.id_usuario, profesional.nombre, profesional.apellido,
             profesional.numero_licencia, profesional.tipo_profesional,
             profesional.numero_contacto, id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404, detail="Profesional no encontrado")
        return {"informacion": "Profesional actualizado con éxito"}
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=500, detail=f"Error de base de datos: {err}")
    finally:
        cursor.close()
        conn.close()


@app.delete("/profesionales/{id}")
def delete_profesional(id: int, token_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM profesionales WHERE id = %s", (id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404, detail="Profesional no encontrado")
        return {"informacion": "Profesional eliminado con éxito"}
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=500, detail=f"Error de base de datos: {err}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
