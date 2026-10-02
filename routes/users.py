import os
import secrets

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel import Session, select

from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token, verify_access_token
from auth.rbac import RoleChecker
from database.connection import get_session
from models.users import MFARequest, User, UserAdminCreate, UserCreate

user_router = APIRouter(tags=["Users"])
hash_password = HashPassword()
allow_admin = RoleChecker(["admin"])
MFA_CODE = os.getenv("MFA_CODE", "123456")
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"

async def oauth2_credentials(
    username: str = Form(...),
    password: str = Form(...),
):
    return {"username": username, "password": password}

def token_response(access_token: str) -> JSONResponse:
    response = JSONResponse(
        content={"access_token": access_token, "token_type": "Bearer"}
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        max_age=3600,
    )
    return response

@user_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def sign_user_up(
    data: UserCreate,
    session: Session = Depends(get_session),
):
    user_exist = session.exec(select(User).where(User.email == data.email)).first()
    if user_exist:
        raise HTTPException(status_code=409, detail="Email já cadastrado.")

    user = User(
        name=data.name,
        email=data.email,
        password=hash_password.create_hash(data.password),
        role="recepcionista",
    )
    session.add(user)
    session.commit()
    return {"message": "Usuário criado com sucesso!"}

@user_router.post("/signin")
async def sign_user_in(
    form_data: dict = Depends(oauth2_credentials),
    session: Session = Depends(get_session),
):
    user = session.exec(
        select(User).where(User.email == form_data.get("username"))
    ).first()
    if not user or not hash_password.verify_hash(
        form_data.get("password", ""),
        user.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas.",
        )

    if user.role == "admin":
        mfa_token = create_access_token(
            user.email,
            expires_in=300,
            mfa_verified=False,
            token_type="mfa",
        )
        return {
            "mfa_required": True,
            "mfa_token": mfa_token,
            "message": "Informe o código MFA em /user/mfa.",
        }

    return token_response(
        create_access_token(user.email, mfa_verified=True)
    )

@user_router.post("/mfa")
async def verify_mfa(
    data: MFARequest,
    session: Session = Depends(get_session),
):
    token_data = verify_access_token(data.mfa_token)
    if (
        not token_data
        or token_data.get("token_type") != "mfa"
        or not secrets.compare_digest(data.code, MFA_CODE)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código ou token MFA inválido",
        )

    user = session.exec(
        select(User).where(User.email == token_data["user"])
    ).first()
    if not user or user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="MFA disponível somente para administradores",
        )

    return token_response(
        create_access_token(user.email, mfa_verified=True)
    )

@user_router.get("/admin")
async def admin_only(current_user: User = Depends(allow_admin)):
    return {"message": "Acesso administrativo autorizado"}


@user_router.post("/admin/users", status_code=status.HTTP_201_CREATED)
async def create_user_by_admin(
    data: UserAdminCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(allow_admin),
):
    user_exist = session.exec(select(User).where(User.email == data.email)).first()
    if user_exist:
        raise HTTPException(status_code=409, detail="Email já cadastrado.")
    user = User(
        name=data.name,
        email=data.email,
        password=hash_password.create_hash(data.password),
        role=data.role,
    )
    session.add(user)
    session.commit()
    return {"message": "Usuário criado com sucesso!"}
