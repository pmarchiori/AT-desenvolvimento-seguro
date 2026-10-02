from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/signin", auto_error=False)

async def authenticate(
    request: Request,
    bearer_token: Optional[str] = Depends(oauth2_scheme),
) -> dict:
    decoded_token = getattr(request.state, "token_data", None)
    if not decoded_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token ausente",
        )
    if decoded_token.get("actor_type") != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token de usuário obrigatório",
        )
    return decoded_token
