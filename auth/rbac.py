from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

from auth.authenticate import authenticate
from database.connection import get_session
from models.users import User

class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        token_data: dict = Depends(authenticate),
        session: Session = Depends(get_session),
    ) -> User:
        email = token_data["user"]
        user = session.exec(select(User).where(User.email == email)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado",
            )
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Seu perfil ({user.role}) não tem permissão para esta ação.",
            )
        if user.role == "admin" and not token_data.get("mfa_verified"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="MFA obrigatório para contas administrativas",
            )
        return user
