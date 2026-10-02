from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.security.utils import get_authorization_scheme_param
from starlette.middleware.base import BaseHTTPMiddleware

from auth.jwt_handler import verify_access_token

class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.token_data = None
        authorization = request.headers.get("Authorization", "")
        scheme, token = get_authorization_scheme_param(authorization)
        if not token:
            token = request.cookies.get("access_token")

        if (scheme.lower() == "bearer" or not scheme) and token:
            token_data = verify_access_token(token)
            if not token_data:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Token inválido ou expirado"},
                )
            request.state.token_data = token_data

        return await call_next(request)
