from fastapi import FastAPI
from .routers import tasks # routers 패키지의 tasks 모듈을 가져옵니다.

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(title="ToDo List API - 실전 프로젝트")

# tasks 라우터를 메인 앱에 포함시킵니다.
app.include_router(
    tasks.router,       # 포함할 라우터 객체
    prefix="/tasks",    # 이 라우터의 모든 경로 앞에 "/tasks" 를 붙입니다.
    tags=["Tasks"]      # API 문서에서 "Tasks" 라는 태그로 그룹화합니다.
)
# 나중에 사용자 관련 라우터가 생기면 아래처럼 추가할 수 있습니다.
# from .routers import users
# app.include_router(users.router, prefix="/users", tags=["Users"])


@app.get("/")
async def root():
    # 간단한 루트 엔드포인트
    return {"message": "Welcome to the ToDo List API!"}

