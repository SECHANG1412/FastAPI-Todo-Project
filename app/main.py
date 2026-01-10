# app/main.py

from fastapi import FastAPI
from .routers import tasks  # app/routers 폴더 안에 있는 tasks.py 파일을 가져온다 → 할 일(Task) 관련 기능들이 들어 있는 파일


# FastAPI 애플리케이션(서버) 객체를 하나 만든다
# title은 API 설명서(Swagger)에 표시될 서버 이름
app = FastAPI(title="ToDo List API - 실전 프로젝트")


# tasks.py에 정의된 router를
# 이 메인 FastAPI 앱에 연결(include)해준다.
app.include_router(
    tasks.router,       # tasks.py 안에 있는 router 객체 → 할 일 생성, 조회, 수정, 삭제 기능들이 묶여 있음
    prefix="/tasks",    # 이 라우터에 속한 모든 주소 앞에 "/tasks"를 붙여준다
    tags=["Tasks"]      # API 설명서에서 "Tasks"라는 묶음으로 보이게 해준다
)


# 나중에 사용자 관련 라우터가 생기면 아래처럼 추가할 수 있습니다.
# from .routers import users
# app.include_router(users.router, prefix="/users", tags=["Users"])


# 루트(root) 경로 함수
# 아직 app.get("/") 같은 데코레이터가 없어서 실제로는 호출되지 않는 상태
@app.get("/")
async def root():
    return {"message": "Welcome to the ToDo List API!"}
    # JSON 형태의 메시지를 반환
    # → "이 API에 오신 걸 환영합니다"라는 뜻