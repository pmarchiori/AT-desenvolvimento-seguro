from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel import Session, select

from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token
from database.connection import get_session
from models.users import User

user_router = APIRouter(tags=["Users"])
hash_password = HashPassword()

async def oauth2_credentials(
    username: str = Form(...),
    password: str = Form(...),
):
    return {"username": username, "password": password}

@user_router.post("/signup")
async def sign_user_up(user: User, session: Session = Depends(get_session)):
    user_exist = session.exec(select(User).where(User.email == user.email)).first()
    if user_exist:
        raise HTTPException(status_code=409, detail="Email já cadastrado.")
    user.password = hash_password.create_hash(user.password)
    session.add(user)
    session.commit()
    return {"message": "Usuário criado com sucesso!"}

@user_router.post("/signin")
async def sign_user_in(
    form_data: dict = Depends(oauth2_credentials),
    session: Session = Depends(get_session),
):
    user_exist = session.exec(
        select(User).where(User.email == form_data.get("username"))
    ).first()
    if not user_exist or not hash_password.verify_hash(
        form_data.get("password", ""),
        user_exist.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas.",
        )
    access_token = create_access_token(user_exist.email)
    response = JSONResponse(
        content={"access_token": access_token, "token_type": "Bearer"}
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
    )
    return response
