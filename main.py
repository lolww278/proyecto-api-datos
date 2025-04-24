from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)


# Inicializamos la aplicación FastAPI
app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir solicitudes desde ambos puertos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conexión a la base de datos MySQL con manejo de errores
try:
    mydb = mysql.connector.connect(
        host="blopeqwmnjnb4wooylcu-mysql.services.clever-cloud.com",
        user="uipu4afryxtg3ny1",
        password="TLOXVsR7nwbjq5LBdIgI",
        database="blopeqwmnjnb4wooylcu"
    )
    print("Conexión exitosa a la base de datos")
except mysql.connector.Error as err:
    print(f"Error al conectar con la base de datos: {err}")

# ✅ Modelo de Usuario para Pydantic
class Usuario(BaseModel):
    email: str
    nombre_c: str
    rol: str  
    genero: str  

# ✅ Obtener todos los usuarios
@app.get("/usuarios")
def get_all_usuarios():
    try:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios")
        usuarios = cursor.fetchall()
        cursor.close()
        return {"resultado": jsonable_encoder(usuarios)}
    except Exception as error:
        return {"error": str(error)}

# ✅ Obtener usuario por ID
@app.get("/usuarios/{id}")
def get_usuario_by_id(id: int):
    try:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
        usuario = cursor.fetchone()
        cursor.close()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return {"resultado": jsonable_encoder(usuario)}
    except Exception as error:
        return {"error": str(error)}

# ✅ Insertar un nuevo usuario
@app.post("/usuarios")
def add_usuario(usuario: Usuario):
    try:
        cursor = mydb.cursor()
        cursor.execute("""
            INSERT INTO usuarios (email, nombre_c, rol, genero)
            VALUES (%s, %s, %s, %s)
        """, (usuario.email, usuario.nombre_c, usuario.rol, usuario.genero))
        mydb.commit()
        cursor.close()
        return {"informacion": "Usuario registrado con éxito"}
    except Exception as error:
        return {"error": str(error)}

# ✅ Actualizar un usuario por ID
@app.put("/usuarios/{id}")
def update_usuario(id: int, usuario: Usuario):
    try:
        cursor = mydb.cursor()
        cursor.execute("""
            UPDATE usuarios
            SET email = %s, nombre_c = %s, rol = %s, genero = %s
            WHERE id = %s
        """, (usuario.email, usuario.nombre_c, usuario.rol, usuario.genero, id))
        mydb.commit()
        cursor.close()
        return {"informacion": "Usuario actualizado con éxito"}
    except Exception as error:
        return {"error": str(error)}

# ✅ Eliminar un usuario por ID
@app.delete("/usuarios/{id}")
def delete_usuario(id: int):
    try:
        cursor = mydb.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
        mydb.commit()
        cursor.close()
        return {"informacion": "Usuario eliminado con éxito"}
    except Exception as error:
        return {"error": str(error)}

#___________________________________________________
#PACIENTES

class Paciente(BaseModel):
    id_usuario: int
    nombre: str
    apellido: str
    fecha_nacimiento: str  # Formato YYYY-MM-DD
    genero: str  # 'Masculino', 'Femenino', 'Otro'
    numero_contacto: str
    direccion: str

# Ruta para obtener todos los pacientes
@app.get("/pacientes")
def get_all_pacientes():
    try:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pacientes")
        pacientes = cursor.fetchall()
        cursor.close()
        return {"resultado": jsonable_encoder(pacientes)}
    except Exception as error:
        return {"error": str(error)}

# Ruta para obtener paciente por ID
@app.get("/pacientes/{id}")
def get_paciente_by_id(id: int):
    try:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pacientes WHERE id = %s", (id,))
        paciente = cursor.fetchone()
        cursor.close()
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        return {"resultado": jsonable_encoder(paciente)}
    except Exception as error:
        return {"error": str(error)}

# Ruta para insertar un nuevo paciente
@app.post("/pacientes")
def add_paciente(paciente: Paciente):
    try:
        cursor = mydb.cursor()
        cursor.execute("""
            INSERT INTO pacientes (id_usuario, nombre, apellido, fecha_nacimiento, genero, numero_contacto, direccion)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (paciente.id_usuario, paciente.nombre, paciente.apellido, paciente.fecha_nacimiento, paciente.genero, paciente.numero_contacto, paciente.direccion))
        mydb.commit()
        cursor.close()
        return {"informacion": "Paciente registrado con éxito"}
    except Exception as error:
        return {"error": str(error)}

# Ruta para actualizar un paciente por ID
@app.put("/pacientes/{id}")
def update_paciente(id: int, paciente: Paciente):
    try:
        cursor = mydb.cursor()
        cursor.execute("""
            UPDATE pacientes
            SET id_usuario = %s, nombre = %s, apellido = %s, fecha_nacimiento = %s, genero = %s, numero_contacto = %s, direccion = %s
            WHERE id = %s
        """, (paciente.id_usuario, paciente.nombre, paciente.apellido, paciente.fecha_nacimiento, paciente.genero, paciente.numero_contacto, paciente.direccion, id))
        mydb.commit()
        cursor.close()
        return {"informacion": "Paciente actualizado con éxito"}
    except Exception as error:
        return {"error": str(error)}

# Ruta para eliminar un paciente por ID
@app.delete("/pacientes/{id}")
def delete_paciente(id: int):
    try:
        cursor = mydb.cursor()
        cursor.execute("DELETE FROM pacientes WHERE id = %s", (id,))
        mydb.commit()
        cursor.close()
        return {"informacion": "Paciente eliminado con éxito"}
    except Exception as error:
        return {"error": str(error)}

#_______________PROFESIONALES

class Profesional(BaseModel):
    id_usuario: int
    nombre: str
    apellido: str
    numero_licencia: str
    tipo_profesional: str  # 'psicologo' o 'psiquiatra'
    numero_contacto: str

# Ruta para obtener todos los profesionales
@app.get("/profesionales")
def get_all_profesionales():
    try:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM profesionales")
        profesionales = cursor.fetchall()
        cursor.close()
        return {"resultado": jsonable_encoder(profesionales)}
    except Exception as error:
        return {"error": str(error)}

# Ruta para obtener profesional por ID
@app.get("/profesionales/{id}")
def get_profesional_by_id(id: int):
    try:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM profesionales WHERE id = %s", (id,))
        profesional = cursor.fetchone()
        cursor.close()
        if not profesional:
            raise HTTPException(status_code=404, detail="Profesional no encontrado")
        return {"resultado": jsonable_encoder(profesional)}
    except Exception as error:
        return {"error": str(error)}

# Ruta para insertar un nuevo profesional
@app.post("/profesionales")
def add_profesional(profesional: Profesional):
    try:
        cursor = mydb.cursor()
        cursor.execute("""
            INSERT INTO profesionales (id_usuario, nombre, apellido, numero_licencia, tipo_profesional, numero_contacto)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (profesional.id_usuario, profesional.nombre, profesional.apellido, profesional.numero_licencia, profesional.tipo_profesional, profesional.numero_contacto))
        mydb.commit()
        cursor.close()
        return {"informacion": "Profesional registrado con éxito"}
    except Exception as error:
        return {"error": str(error)}

# Ruta para actualizar un profesional por ID
@app.put("/profesionales/{id}")
def update_profesional(id: int, profesional: Profesional):
    try:
        cursor = mydb.cursor()
        cursor.execute("""
            UPDATE profesionales
            SET id_usuario = %s, nombre = %s, apellido = %s, numero_licencia = %s, tipo_profesional = %s, numero_contacto = %s
            WHERE id = %s
        """, (profesional.id_usuario, profesional.nombre, profesional.apellido, profesional.numero_licencia, profesional.tipo_profesional, profesional.numero_contacto, id))
        mydb.commit()
        cursor.close()
        return {"informacion": "Profesional actualizado con éxito"}
    except Exception as error:
        return {"error": str(error)}

# Ruta para eliminar un profesional por ID
@app.delete("/profesionales/{id}")
def delete_profesional(id: int):
    try:
        cursor = mydb.cursor()
        cursor.execute("DELETE FROM profesionales WHERE id = %s", (id,))
        mydb.commit()
        cursor.close()
        return {"informacion": "Profesional eliminado con éxito"}
    except Exception as error:
        return {"error": str(error)}

