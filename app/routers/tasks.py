# app/routers/tasks.py

from fastapi import APIRouter, HTTPException, status, Path
from typing import List
from ..models.task import Task, TaskCreate


router = APIRouter()    # APIRouter 객체를 하나 만든다 → 이 파일 전체가 하나의 API 묶음이 됨


tasks_db = {}       # 실제 DB 대신 쓰는 가짜 데이터 저장소 → Key: task_id, value: Task 객체
next_task_id = 1    # 다음에 만들 Task에 붙일 번호 → Task 하나 만들 때마다 1씩 증가


# POST 요청 (할 일 새로 만들기)
# "/" → 이 라우터의 기본 경로
# response_model=Task → 응답은 Task 모양으로 나간다
# status_code=201 → "성공적으로 생성됨" 이라는 뜻
@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate # 사용자가 보내는 데이터 → TaskCreate 규칙을 반드시 만족해야 함
):
    global next_task_id                 # 함수 안에서 전역 변수 next_task_id를 쓰겠다고 선언

    # 새 Task 객체를 만든다
    new_task = Task(    
        id=next_task_id,                # id → 자동으로 붙여줌
        **task_in.model_dump(),         # **task_in.model_dump() → title, description 꺼내서 넣기
        completed=False                 # completed=False → 처음엔 무조건 미완료
    )

    tasks_db[next_task_id] = new_task   # 만든 Task를 DB(딕셔너리)에 저장
    next_task_id += 1                   # 다음 Task를 위해 번호 1 증가
    print(f"Task created: {new_task}")  # 콘솔에 로그 출력 (디버깅용)
    return new_task                     # 만든 Task를 사용자에게 돌려줌




# GET 요청 (모든 할 일 조회)
# reponse_model=List[Task] → Task 여러 개를 리스트로 반환
@router.get("/", response_model=List[Task])
async def read_tasks():
    print(f"Reading all tasks: {list(tasks_db.values())}")  # 현재 저장된 모든 Task를 콘솔에 출력
    return list(tasks_db.values())                          # DB에 있는 Task들만 리스트로 만들어서 반환




# GET 요청 (특정 할 일 하나 조회)
# URL 예: /tasks/1
@router.get("/{task_id}", response_model=Task)
async def read_task(
    task_id: int = Path(..., title="조회할 Task의 ID", ge=1)
    # task_id는 URL 경로에서 받아오는 숫자
    # Path(...) → 반드시 있어야 함
    # title → API 문서에 표시될 설명
    # ge=1 → 1 이상만 허용
):
    
    # 만약 해당 ID가 DB에 없다면
    if task_id not in tasks_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        # 404 에러를 일부러 발생시킴

    print(f"Reading task: {tasks_db[task_id]}") # 정상이라면 해당 Task를 콘솔에 출력
    return tasks_db[task_id]                    # 해당 Task 반환




# PUT 요청 (기존 할 일 수정)
@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_update: TaskCreate,                                    # 수정할 내용 (title, description)
    task_id: int = Path(..., title="수정할 Task의 ID", ge=1)    # 수정할 대상의 ID
):
    
    # 해당 ID가 없다면
    if task_id not in tasks_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        # 404 에러 발생

    existing_task = tasks_db[task_id]                       # 기존 Task를 가져옴
    existing_task.title = task_update.title                 # 제목 수정
    existing_task.description = task_update.description     # 설명 수정

    print(f"Task updated: {existing_task}")                 # 수정 완료 로그 출력
    return existing_task                                    # 수정된 Task 반환



# DELETE 요청 (할 일 삭제)
# 성공 시 204 → 내용 없음 (돌려줄 데이터 없음)
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int = Path(..., title="삭제할 Task의 ID", ge=1)    # 삭제할 Task의 ID
):
    
    # 해당 ID가 없다면 
    if task_id not in tasks_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found") # 404 에러 발생
    
    del tasks_db[task_id]                   # DB에서 해당 Task 삭제

    print(f"Task deleted: ID={task_id}")    # 삭제 로그 출력
    return None                             # 204 응답은 반환값이 없어야 하므로 None 반환