"""
Authentication Routes - REAL IMPLEMENTATION
Google OAuth and JWT authentication
"""
from typing import Optional
from datetime import datetime
from urllib.parse import urlencode
import httpx

from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr

from src.config.settings import settings
from src.application.services.auth_service import AuthService

router = APIRouter()
security = HTTPBearer(auto_error=False)
auth_service = AuthService()


# Request/Response Models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None
    subscription_tier: str = "free"
    gmail_connected: bool = False


# Dependency for getting current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Get current authenticated user from JWT token."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    payload = auth_service.decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    user = await auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    """
    Register a new user with email and password.
    
    Returns access and refresh tokens upon successful registration.
    """
    try:
        user = await auth_service.create_user(
            email=request.email,
            password=request.password,
            name=request.name,
        )
        
        # Generate tokens
        access_token = auth_service.create_access_token(
            data={"sub": user["id"], "email": user["email"], "type": "access"}
        )
        refresh_token = auth_service.create_refresh_token(user["id"])
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.jwt_expiration_hours * 3600,
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Login with email and password.
    
    Returns access and refresh tokens upon successful authentication.
    """
    user = await auth_service.authenticate_user(
        email=request.email,
        password=request.password,
    )
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    access_token = auth_service.create_access_token(
        data={"sub": user["id"], "email": user["email"], "type": "access"}
    )
    refresh_token = auth_service.create_refresh_token(user["id"])
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_expiration_hours * 3600,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshRequest):
    """
    Refresh access token using refresh token.
    """
    new_access_token = await auth_service.refresh_access_token(request.refresh_token)
    
    if not new_access_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=request.refresh_token,
        expires_in=settings.jwt_expiration_hours * 3600,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user)
):
    """
    Get current authenticated user's profile.
    """
    return UserResponse(**current_user)


# ===========================================
# Google OAuth
# ===========================================

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# OAuth scopes
SCOPES = [
    "openid",
    "email",
    "profile",
    "https://www.googleapis.com/auth/gmail.readonly",
]


@router.get("/google")
async def google_oauth_initiate():
    """
    Initiate Google OAuth flow.
    
    Returns the URL to redirect the user to for Google authentication.
    """
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(
            status_code=500,
            detail="Google OAuth is not configured"
        )
    
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": "moneymind_oauth",  # Add CSRF protection in production
    }
    
    auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    
    return {"auth_url": auth_url}


@router.get("/google/callback")
async def google_oauth_callback(
    code: Optional[str] = None,
    error: Optional[str] = None,
    state: Optional[str] = None,
):
    """
    Handle Google OAuth callback.
    
    Exchanges authorization code for tokens and creates/updates user.
    Returns access and refresh tokens.
    """
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
    
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code required")
    
    # Verify state (CSRF protection)
    if state != "moneymind_oauth":
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    try:
        async with httpx.AsyncClient() as client:
            # Exchange code for tokens
            token_response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "code": code,
                    "redirect_uri": settings.google_redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            
            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail=f"Token exchange failed: {token_response.text}"
                )
            
            token_data = token_response.json()
            google_access_token = token_data.get("access_token")
            google_refresh_token = token_data.get("refresh_token")
            
            # Get user info
            userinfo_response = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {google_access_token}"},
            )
            
            if userinfo_response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to get user info"
                )
            
            userinfo = userinfo_response.json()
            
            # Authenticate/create user
            user = await auth_service.authenticate_google(
                google_id=userinfo.get("id"),
                email=userinfo.get("email"),
                name=userinfo.get("name"),
                picture=userinfo.get("picture"),
                refresh_token=google_refresh_token,
            )
            
            # Generate our tokens
            access_token = auth_service.create_access_token(
                data={"sub": user["id"], "email": user["email"], "type": "access"}
            )
            refresh_token = auth_service.create_refresh_token(user["id"])
            
            # Return tokens (frontend should handle this)
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "name": user["name"],
                    "picture": user["picture"],
                    "gmail_connected": user["gmail_connected"],
                },
            }
            
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"OAuth request failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@router.post("/logout")
async def logout(
    current_user: dict = Depends(get_current_user)
):
    """
    Logout user.
    
    Note: JWT tokens are stateless, so logout is handled client-side
    by removing the tokens. This endpoint is for any server-side cleanup.
    """
    # TODO: Add token to blacklist if implementing token revocation
    return {"message": "Logged out successfully"}
