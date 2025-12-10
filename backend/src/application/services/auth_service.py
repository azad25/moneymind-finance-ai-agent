"""
Auth Service - REAL IMPLEMENTATION
JWT authentication and user management
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import uuid

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select

from src.config.settings import settings


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for authentication operations."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours)
        
        to_encode.update({"exp": expire})
        
        return jwt.encode(
            to_encode,
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )
    
    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        """Create a refresh token with longer expiry."""
        return AuthService.create_access_token(
            data={"sub": user_id, "type": "refresh"},
            expires_delta=timedelta(days=30),
        )
    
    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm],
            )
            return payload
        except JWTError:
            return None
    
    async def create_user(
        self,
        email: str,
        password: Optional[str] = None,
        name: Optional[str] = None,
        google_id: Optional[str] = None,
        picture: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new user."""
        from src.infrastructure.database.postgres import async_session_factory
        from src.domain.models.user import User
        
        async with async_session_factory() as session:
            # Check if user exists
            existing = await session.execute(
                select(User).where(User.email == email)
            )
            if existing.scalar_one_or_none():
                raise ValueError("User with this email already exists")
            
            # Create user
            user_id = str(uuid.uuid4())
            user = User(
                id=user_id,
                email=email,
                password_hash=self.hash_password(password) if password else None,
                name=name,
                google_id=google_id,
                picture=picture,
                is_active=True,
                is_verified=bool(google_id),  # Google users are auto-verified
            )
            
            session.add(user)
            await session.commit()
            
            return {
                "id": user_id,
                "email": email,
                "name": name,
            }
    
    async def authenticate_user(
        self,
        email: str,
        password: str,
    ) -> Optional[Dict[str, Any]]:
        """Authenticate user with email and password."""
        from src.infrastructure.database.postgres import async_session_factory
        from src.domain.models.user import User
        
        async with async_session_factory() as session:
            result = await session.execute(
                select(User).where(User.email == email)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            if not user.password_hash:
                return None  # OAuth-only user
            
            if not self.verify_password(password, user.password_hash):
                return None
            
            if not user.is_active:
                return None
            
            # Update last login
            user.last_login_at = datetime.utcnow()
            await session.commit()
            
            return {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "subscription_tier": user.subscription_tier,
            }
    
    async def authenticate_google(
        self,
        google_id: str,
        email: str,
        name: Optional[str] = None,
        picture: Optional[str] = None,
        refresh_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Authenticate or create user via Google OAuth."""
        from src.infrastructure.database.postgres import async_session_factory
        from src.domain.models.user import User
        
        async with async_session_factory() as session:
            # Check for existing user by Google ID
            result = await session.execute(
                select(User).where(User.google_id == google_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                # Check by email
                result = await session.execute(
                    select(User).where(User.email == email)
                )
                user = result.scalar_one_or_none()
                
                if user:
                    # Link Google account to existing user
                    user.google_id = google_id
                    user.picture = picture or user.picture
                    if refresh_token:
                        user.google_refresh_token = refresh_token
                else:
                    # Create new user
                    user = User(
                        id=str(uuid.uuid4()),
                        email=email,
                        name=name,
                        google_id=google_id,
                        picture=picture,
                        google_refresh_token=refresh_token,
                        is_active=True,
                        is_verified=True,
                    )
                    session.add(user)
            else:
                # Update existing user
                user.name = name or user.name
                user.picture = picture or user.picture
                if refresh_token:
                    user.google_refresh_token = refresh_token
            
            user.last_login_at = datetime.utcnow()
            await session.commit()
            
            return {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "picture": user.picture,
                "subscription_tier": user.subscription_tier,
                "gmail_connected": bool(user.google_refresh_token),
            }
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        from src.infrastructure.database.postgres import async_session_factory
        from src.domain.models.user import User
        
        async with async_session_factory() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            return {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "picture": user.picture,
                "subscription_tier": user.subscription_tier,
                "gmail_connected": bool(user.google_refresh_token),
                "created_at": user.created_at.isoformat() if user.created_at else None,
            }
    
    async def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Refresh access token using refresh token."""
        payload = self.decode_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        # Verify user still exists and is active
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Create new access token
        return self.create_access_token(
            data={
                "sub": user_id,
                "email": user.get("email"),
                "type": "access",
            }
        )
