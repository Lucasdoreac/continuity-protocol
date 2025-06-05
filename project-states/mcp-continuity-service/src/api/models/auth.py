"""
Authentication Models - MCP Continuity Service
JWT-based auth with user management
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import os

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET", "mcp-continuity-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Pydantic Models
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str
    plan: str = "free"  # free, pro, enterprise


class UserLogin(BaseModel):
    username: str
    password: str


class User(UserBase):
    id: Optional[int] = None
    plan: str = "free"
    api_calls_used: int = 0
    api_calls_limit: int = 100
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES * 60
    user: Optional[User] = None


class TokenData(BaseModel):
    username: Optional[str] = None


# Authentication Functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            return None
            
        return TokenData(username=username)
    except JWTError:
        return None


# Plan Models
class PlanLimits(BaseModel):
    name: str
    api_calls_per_month: int
    sessions_limit: int
    features: List[str]
    price_usd: float


# Predefined Plans
PLANS = {
    "free": PlanLimits(
        name="Free",
        api_calls_per_month=100,
        sessions_limit=5,
        features=["Basic continuity", "5 sessions", "Community support"],
        price_usd=0.0
    ),
    "pro": PlanLimits(
        name="Pro",
        api_calls_per_month=1000,
        sessions_limit=50,
        features=[
            "Advanced continuity", "50 sessions", "Priority support",
            "API access", "Custom integrations"
        ],
        price_usd=9.99
    ),
    "enterprise": PlanLimits(
        name="Enterprise",
        api_calls_per_month=10000,
        sessions_limit=999,
        features=[
            "Unlimited continuity", "Unlimited sessions", "24/7 support",
            "Full API access", "Custom deployment", "SLA guarantee"
        ],
        price_usd=49.99
    )
}


def get_plan_limits(plan_name: str) -> PlanLimits:
    """Get plan limits by name"""
    return PLANS.get(plan_name, PLANS["free"])


def check_api_limit(user: User) -> bool:
    """Check if user has exceeded API limits"""
    plan_limits = get_plan_limits(user.plan)
    return user.api_calls_used < plan_limits.api_calls_per_month


def increment_api_usage(user: User) -> User:
    """Increment user API usage"""
    user.api_calls_used += 1
    user.last_login = datetime.utcnow()
    return user
