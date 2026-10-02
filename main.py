import uvicorn
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()

from auth.jwt_middleware import JWTMiddleware
from database.connection import conn
from routes.appointments import appointment_router
from routes.integrations import integration_router
from routes.patients import patient_router
from routes.users import user_router
from security.http import LoginRateLimitMiddleware, SecurityHeadersMiddleware

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip() and origin.strip() != "*"
]

app = FastAPI(
    title="API de Agendamento Clínico",
    on_startup=[conn],
)
app.add_middleware(JWTMiddleware)
app.add_middleware(LoginRateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.add_middleware(SecurityHeadersMiddleware)

app.include_router(user_router, prefix="/user")
app.include_router(patient_router, prefix="/patient")
app.include_router(appointment_router, prefix="/appointment")
app.include_router(integration_router, prefix="/oauth")

@app.get("/")
async def home():
    return {"message": "Bem-vindo à API da Clínica!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
