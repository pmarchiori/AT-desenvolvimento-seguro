import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
load_dotenv()

from database.connection import conn
from routes.appointments import appointment_router
from routes.patients import patient_router
from routes.users import user_router

app = FastAPI(
    title="API de Agendamento Clínico",
    on_startup=[conn],
)

app.include_router(user_router, prefix="/user")
app.include_router(patient_router, prefix="/patient")
app.include_router(appointment_router, prefix="/appointment")

@app.get("/")
async def home():
    return {"message": "Bem-vindo à API da Clínica!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
