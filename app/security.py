# app/security.py

import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .database import get_db
from .sql_models.user import User as SQLAlchemyUser

from .schemas.token import TokenData



pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto"
)



def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)



SECRET_KEY = os.getenv("SECRET_KEY", "a_very_secret_key_that_should_be_in_env_var_or_secret_manager_0123456789abcdef")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),    
    db: AsyncSession = Depends(get_db)   
) -> SQLAlchemyUser:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")

        if email is None:
            print("JWT 'sub' claim missing")
            raise credentials_exception
        
        token_data = TokenData(email=email)
    
    except JWTError as e:
        print(f"JWT Error during decoding: {e}")
        raise credentials_exception
    
    query = select(SQLAlchemyUser).where(
        SQLAlchemyUser.email == token_data.email
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        print(f"User not found in DB for email from token: {token_data.email}")
        raise credentials_exception
    
    return user


async def require_admin(
        current_user: SQLAlchemyUser = Depends(get_current_user)
) -> SQLAlchemyUser:
    if not current_user.is_admin:
        print(f"Forbidden: User '{current_user.email}' is not an admin.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator privileges required",
        )
    
    return current_user
