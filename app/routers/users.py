# app/routers/users.py


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.user import User as PydanticUser, UserCreate 
from ..sql_models.user import User as SQLAlchemyUser  
from ..database import get_db                           
from ..security import get_password_hash, require_admin
from typing import List


router = APIRouter()

@router.post(
        "/", 
        response_model=PydanticUser,          
        status_code=status.HTTP_201_CREATED,  
        summary="Register new user"
)
async def register_user(
    user_in: UserCreate,                     
    db: AsyncSession = Depends(get_db)        
):
    query = select(SQLAlchemyUser).where(
        SQLAlchemyUser.email == user_in.email
    )

    result = await db.execute(query)

    existing_user = result.scalar_one_or_none()

    if existing_user:
        print(f"Registration failed: Email already exists - {user_in.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    hashed_password = get_password_hash(user_in.password)

    db_user = SQLAlchemyUser(
        email=user_in.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    print(f"User registered successfully: {db_user.email} (ID: {db_user.id})")

    return db_user



@router.get(
        "/all", 
        response_model=List[PydanticUser], 
        summary="Get all users (Admin Only)"
)
async def read_all_users(
    db: AsyncSession = Depends(get_db),
    admin_user: SQLAlchemyUser = Depends(require_admin)
):
    print(f"Admin user '{admin_user.email}' accessing all users list.") 
    query = select(SQLAlchemyUser)
    result = await db.execute(query)
    users = result.scalars().all()
    return users