# app/main.py

from fastapi import FastAPI
from .routers import tasks  # app/routers 폴더 안에 있는 tasks.py 파일을 가져온다 → 할 일(Task) 관련 기능들이 들어 있는 파일
from .routers import users  # 사용자(User) 관련 API 라우터 (회원가입, 로그인 등)


# FastAPI 애플리케이션(서버) 객체 생성
# title은 자동 생성되는 API 문서(Swagger UI)에 표시될 서비스 이름
app = FastAPI(title="ToDo List API - 실전 프로젝트")



# =========================================================
# 할 일(Task) 관련 API 라우터 등록
# =========================================================
# app/routers/tasks.py 안에 정의된 router 객체를
# 메인 FastAPI 앱에 연결(include)한다.
#
# 결과적으로:
# - tasks.py 안의 모든 엔드포인트는
#   /tasks 로 시작하는 URL을 갖게 된다.
#
# 예:
#   GET  /tasks/
#   POST /tasks/
#   PUT  /tasks/{id}
app.include_router(
    tasks.router,       # tasks.py에 정의된 APIRouter 객체
    prefix="/tasks",    # 이 라우터의 모든 경로 앞에 "/tasks"를 붙임
    tags=["Tasks"]      # Swagger UI에서 "Tasks" 그룹으로 묶어 표시
)


# =========================================================
# 사용자(User) 관련 API 라우터 등록 (새로 추가된 부분)
# =========================================================
# app/routers/users.py 안에 정의된 router 객체를
# 메인 FastAPI 앱에 연결(include)한다.
#
# 이 라우터는:
# - 사용자 회원가입
# - (추후) 로그인, 사용자 인증 관련 API
# 를 담당한다.
#
# prefix="/users" 를 사용함으로써
# users.py 안의 모든 엔드포인트는
# 반드시 "/users" 로 시작하게 된다.
#
# 예:
#   POST /users/        → 사용자 회원가입
#   GET  /users/{id}    → 사용자 정보 조회 (추후 구현 가능)
app.include_router(
    users.router,       # users.py에 정의된 APIRouter 객체
    prefix="/users",    # 모든 사용자 관련 API의 공통 URL 경로
    tags=["Users"]      # Swagger UI에서 "Users" 그룹으로 표시
)


# =========================================================
# 루트(root) 엔드포인트
# =========================================================
# 서버가 정상적으로 실행 중인지 확인하기 위한 기본 엔드포인트
@app.get("/")
async def root():
    return {"message": "Welcome to the ToDo List API!"}
    # JSON 형태의 메시지를 반환
    # → "이 API에 오신 걸 환영합니다"라는 뜻