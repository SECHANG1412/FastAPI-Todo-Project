# alembic/env.py

# Alembic이 실행될 때 가장 먼저 읽는 설정 파일
# “DB를 어떻게 고칠지”를 정해주는 핵심 파일


import asyncio   # 비동기(async) 함수를 실행하기 위한 도구
import os        # 파일/폴더 경로를 다루기 위한 기본 도구
import sys       # 파이썬이 모듈을 어디서 찾을지 경로를 조작하기 위한 도구

from logging.config import fileConfig                       # Alembic 로그 설정을 읽어서 출력 형태를 맞춰주는 도구
from sqlalchemy import pool                                 # DB 연결 풀(pool)을 관리하기 위한 SQLAlchemy 도구
from sqlalchemy.ext.asyncio import async_engine_from_config # 비동기 DB 엔진을 설정 파일(alembic.ini) 기반으로 만드는 함수
from alembic import context                                 # Alembic이 현재 “마이그레이션 상황”을 관리하는 핵심 객체


# 현재 파일(env.py)이 있는 위치 기준으로, 프로젝트 최상위 폴더를 파이썬 경로(sys.path)에 추가
# 그래야 app.database, app.sql_models 같은 모듈을 찾을 수 있음
sys.path.insert(
    0,
    os.path.realpath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)


# 우리가 만든 SQLAlchemy Base 객체 불러오기
# 모든 테이블 설계도(metadata)가 여기에 들어 있음
from app.database import Base

# Task 모델 파일을 강제로 import
# 그래야 Base.metadata 안에 tasks 테이블 정보가 등록됨
import app.sql_models.task


# alembic.ini 파일 내용을 읽어서 config 객체로 가져옴
# DB 주소(sqlalchemy.url) 같은 설정이 여기에 있음
config = context.config


# alembic.ini에 로깅 설정이 있으면
# 그 설정을 기반으로 로그 출력 형식 적용
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Alembic이 비교 기준으로 삼을 “설계도”
# 즉, 현재 파이썬 모델들이 정의한 테이블 구조 전체
target_metadata = Base.metadata


# =====================================================
# OFFLINE 모드: 실제 DB에 연결하지 않고
# SQL 문장만 만들어내는 모드
# =====================================================
def run_migrations_offline() -> None:
    # alembic.ini에 적혀 있는 DB 주소 가져오기
    url = config.get_main_option("sqlalchemy.url")

    # Alembic에게
    # “이 주소 기준으로, 이 설계도를 가지고 마이그레이션해”
    # 라고 설정
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,                     # SQL에 값들을 직접 넣어서 출력
        dialect_opts={"paramstyle": "named"},   # SQL 문법 스타일 지정
    )

    # 하나의 트랜잭션(작업 묶음) 시작
    with context.begin_transaction():
        # 마이그레이션 실행
        context.run_migrations()


# =====================================================
# ONLINE 모드에서 실제로 실행될
# “동기 마이그레이션 로직”
# =====================================================
def do_run_migrations(connection):
    # Alembic에게
    # “이 DB 연결로, 이 설계도를 기준으로 작업해”
    # 라고 설정
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )

    # 트랜잭션 시작
    with context.begin_transaction():
        # 실제 마이그레이션 실행
        context.run_migrations()


# =====================================================
# ONLINE 모드: 실제 DB에 연결해서
# 테이블을 만들거나 수정하는 모드 (비동기)
# =====================================================
async def run_migrations_online() -> None:
    # alembic.ini 설정을 읽어서
    # “비동기 DB 엔진” 생성
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),  # alembic.ini 전체 설정
        prefix="sqlalchemy.",                           # sqlalchemy.url 같은 설정 사용
        poolclass=pool.NullPool,                        # 연결 풀 사용 안 함
        future=True,                                    # SQLAlchemy 2.0 스타일 사용
    )

    # 비동기로 DB에 연결
    async with connectable.connect() as connection:
        # 비동기 DB 연결 안에서
        # 동기 마이그레이션 로직(do_run_migrations)을 실행
        await connection.run_sync(do_run_migrations)

    # DB 엔진 연결 완전히 종료
    await connectable.dispose()


# =====================================================
# 현재 Alembic 실행 모드에 따라 분기
# =====================================================
if context.is_offline_mode():
    # 오프라인 모드면, SQL만 생성하는 함수 실행
    run_migrations_offline()
else:
    # 온라인 모드면, 비동기 마이그레이션 함수 실행
    asyncio.run(run_migrations_online())
