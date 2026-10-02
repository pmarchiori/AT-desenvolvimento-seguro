import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
load_dotenv()

from auth.jwt_middleware import JWTMiddleware
from database.connection import conn
from routes.appointments import appointment_router
from routes.integrations import integration_router
from routes.patients import patient_router
from routes.users import user_router

app = FastAPI(
    title="API de Agendamento Clínico",
    on_startup=[conn],
)
app.add_middleware(JWTMiddleware)

app.include_router(user_router, prefix="/user")
app.include_router(patient_router, prefix="/patient")
app.include_router(appointment_router, prefix="/appointment")
app.include_router(integration_router, prefix="/oauth")

@app.get("/")
async def home():
    return {"message": "Bem-vindo à API da Clínica!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
