# app/database.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base


# 우리가 사용할 데이터베이스 주소
# sqlite + aiosqlite 를 사용해서 
# 현재 프로젝트 폴더에 sql_app.db 파일을 만든다는 뜻
DATABASE_URL = "sqlite+aiosqlite:///./sql_app.db"


# 모든 ORM 모델이 상속받을 Base 클래스 정의
Base = declarative_base()