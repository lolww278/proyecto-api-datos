acceder al entorno
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
cd myvenv 
cd .\Scripts\ 
.\activate



pip install fastapi
pip install uvicorn
pip install pydantic
pip install mysql-connector-python

fastapi dev main.py