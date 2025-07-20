from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from passlib.context import CryptContext

from app.schemas.auth import Token, User, UserCreate, UserLogin
from app.api.deps import create_access_token, get_current_user
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Mock user database (replace with real database in production)
fake_users_db = {
    "demo_doctor": {
        "id": "1",
        "username": "demo_doctor",
        "email": "demo@dermamed.com",
        "hashed_password": pwd_context.hash("demo123"),
        "full_name": "Demo Doctor",
        "is_active": True,
        "is_medical_professional": True,
        "license_number": "DEMO123",
        "specialization": "Dermatology"
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    """Authenticate user with username and password"""
    user = fake_users_db.get(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint - returns JWT token"""
    
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user["username"], "user_id": user["id"]},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=User)
async def register(user_create: UserCreate):
    """Register new user (medical professionals only)"""
    
    # Check if user already exists
    if user_create.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Verify medical professional status
    if not user_create.is_medical_professional or not user_create.license_number:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration is limited to licensed medical professionals"
        )
    
    # Create new user (in production, save to database)
    hashed_password = get_password_hash(user_create.password)
    
    # Mock user creation
    new_user = {
        "id": str(len(fake_users_db) + 1),
        "username": user_create.username,
        "email": user_create.email,
        "hashed_password": hashed_password,
        "full_name": user_create.full_name,
        "is_active": True,
        "is_medical_professional": user_create.is_medical_professional,
        "license_number": user_create.license_number,
        "specialization": user_create.specialization,
        "created_at": "2025-01-13T00:00:00"
    }
    
    fake_users_db[user_create.username] = new_user
    
    # Return user without password
    return User(**{k: v for k, v in new_user.items() if k != "hashed_password"})

@router.get("/me", response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    
    # Get full user data
    user_data = fake_users_db.get(current_user["username"])
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return user without password
    return User(**{k: v for k, v in user_data.items() if k != "hashed_password"})