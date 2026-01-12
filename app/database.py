# app/database.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import AsyncGenerator


# --- 데이터베이스 연결 URL ---
# 우리가 사용할 데이터베이스의 "주소"
# sqlite + aiosqlite : 비동기 SQLite 사용
# ./sql_app.db       : 현재 프로젝트 폴더에 DB 파일 생성
DATABASE_URL = "sqlite+aiosqlite:///./sql_app.db"


# --- SQLAlchemy 비동기 엔진 생성 ---
# 엔진은 FastAPI 앱과 데이터베이스를 연결하는 "전선" 역할
engine = create_async_engine(
    DATABASE_URL,   # 위에서 정의한 DB 주소 사용
    echo=True,      # True면 DB에 보내는 SQL을 콘솔에 보여줌 (공부/디버깅용)
    future=True     # SQLAlchemy 최신 스타일 사용 (2.0 호환)
)


# --- 비동기 세션 생성기 (Session Factory) ---
# AsyncSessionLocal은 "세션을 찍어내는 공장"
# 요청이 올 때마다 새로운 세션을 만들어줌
AsyncSessionLocal = sessionmaker(
    bind=engine,                # 어떤 엔진(DB 전선)을 사용할지 지정 
    class_=AsyncSession,        # 비동기 세션 사용
    expire_on_commit=False,     # commit 후에도 객체 값 유지
    autocommit=False,           # 자동 저장 ❌ (직접 commit 해야 함)
    autoflush=False,            # 자동 DB 반영 ❌ (원할 때만 반영)
)


# --- ORM 모델의 Base 클래스 ---
# 모든 SQLAlchemy ORM 모델이 상속받아야 하는 "설계 도화지"
# 이 Base를 상속받은 클래스만 DB 테이블로 인식됨
Base = declarative_base()


# --- 의존성 주입을 위한 DB 세션 제공 함수 ---
# FastAPI 요청 하나당 세션 하나를 만들어서 빌려주는 함수
async def get_db() -> AsyncGenerator[AsyncSession, None]:

    # 세션 공장에서 새 DB 세션 하나를 꺼낸다
    # → "DB랑 대화할 담당자" 생성
    session: AsyncSession = AsyncSessionLocal()

    try:
        # 여기서 yield는 
        # → "세션을 잠깐 빌려주는 순간"
        # FastAPI가 이 세션을 API 함수에 전달해 줌
        yield session

    except Exception as e:
        # 요청 처리 중 문제가 생기면 실행됨
        # 지금까지 한 DB 작업을 전부 취소(되돌림)
        print(f"Session rollback triggered due to exception: {e}")
        await session.rollback()
        raise   # 에러를 다시 위로 던져서 FastAPI가 알게 함

    finally:
        # 요청이 성공하든, 실패하든 무조건 실행됨
        # → 빌려준 세션을 반드시 정리
        print("Closing session")
        await session.close()
