import os
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.openapi.models import OAuthFlows
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param

from auth.jwt_handler import verify_access_token

LAB_SCOPE = "appointments:availability:read"

lab_oauth2_scheme = OAuth2(
    flows=OAuthFlows(
        clientCredentials={
            "tokenUrl": "/oauth/token",
            "scopes": {
                LAB_SCOPE: "Consultar somente horários disponíveis",
            },
        }
    ),
    scheme_name="LaboratoryClientCredentials",
)

async def authenticate_laboratory(
    authorization: str = Depends(lab_oauth2_scheme),
) -> dict:
    scheme, token = get_authorization_scheme_param(authorization)
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Bearer obrigatório",
        )
    token_data = verify_access_token(token)
    expected_client_id = os.getenv("LAB_CLIENT_ID")
    token_scopes = set((token_data or {}).get("scope", "").split())
    if (
        not token_data
        or token_data.get("actor_type") != "laboratory"
        or token_data.get("sub") != expected_client_id
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de laboratório inválido",
        )
    if LAB_SCOPE not in token_scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Escopo insuficiente",
        )
    return token_data
