from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    is_medical_professional: bool = True
    license_number: Optional[str] = None
    specialization: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "dr_smith",
                "email": "dr.smith@hospital.com",
                "password": "SecurePass123!",
                "full_name": "Dr. Jane Smith",
                "is_medical_professional": True,
                "license_number": "MD12345",
                "specialization": "Dermatology"
            }
        }

class User(UserBase):
    id: int
    is_active: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str