# Rotas de Autenticação - MCP Continuity Service
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta, datetime
from typing import List
import os
import json
from jose import JWTError

from ..models.auth import (
    User, UserCreate, UserLogin, Token, UserInDB,
    verify_password, get_password_hash, create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
)

router = APIRouter(prefix="/auth", tags=["authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Database simulado (em produção usar SQLite/PostgreSQL)
USERS_DB_FILE = "data/users.json"
users_db = {}

def load_users():
    """Carregar usuários do arquivo JSON"""
    if os.path.exists(USERS_DB_FILE):
        with open(USERS_DB_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users():
    """Salvar usuários no arquivo JSON"""
    os.makedirs(os.path.dirname(USERS_DB_FILE), exist_ok=True)
    with open(USERS_DB_FILE, 'w') as f:
        json.dump(users_db, f, indent=2, default=str)

# Carregar usuários na inicialização
users_db = load_users()

@router.post("/register", response_model=dict)
async def register(user: UserCreate):
    """Registrar novo usuário"""
    if user.email in users_db:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    user_data = {
        "id": len(users_db) + 1,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "hashed_password": hashed_password,
        "is_active": True,
        "subscription_plan": "free",
        "sessions_used": 0,
        "sessions_limit": 10,
        "created_at": str(datetime.utcnow())
    }
    
    users_db[user.email] = user_data
    save_users()
    
    return {"message": "User registered successfully", "user_id": user_data["id"]}

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login e obter token"""
    user = users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/profile", response_model=User)
async def get_profile(token: str = Depends(oauth2_scheme)):
    """Obter perfil do usuário autenticado"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        from jose import jwt
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = users_db.get(email)
    if user is None:
        raise credentials_exception
    
    return User(**user)

@router.get("/users", response_model=List[User])
async def list_users():
    """Listar todos os usuários (admin only)"""
    return [User(**user) for user in users_db.values()]

@router.put("/subscription")
async def update_subscription(plan: str, token: str = Depends(oauth2_scheme)):
    """Atualizar plano de assinatura"""
    # Validar token e obter usuário
    try:
        from jose import jwt
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        user = users_db.get(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Atualizar limites baseado no plano
    limits = {
        "free": 10,
        "pro": 100, 
        "enterprise": -1  # Ilimitado
    }
    
    if plan not in limits:
        raise HTTPException(status_code=400, detail="Invalid subscription plan")
    
    user["subscription_plan"] = plan
    user["sessions_limit"] = limits[plan]
    save_users()
    
    return {"message": f"Subscription updated to {plan}", "sessions_limit": limits[plan]}
