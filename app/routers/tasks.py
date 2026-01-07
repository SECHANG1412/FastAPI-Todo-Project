# app/routers/tasks.py
from fastapi import APIRouter, HTTPException, status, Path # APIRouter, Path 추가
from typing import List # List 추가
from ..models.task import Task, TaskCreate # 상위 디렉토리의 models.task 에서 모델 가져오기

# APIRouter 인스턴스 생성
# 이 router 객체를 사용하여 경로 작동 함수들을 등록합니다.
router = APIRouter()

# --- (임시) 인메모리 데이터 저장소 ---
# 실제 구현은 18강에서! 여기서는 빈 dict와 counter만 정의.
tasks_db = {} # {task_id: Task 객체}
next_task_id = 1

# --- Task 관련 API 엔드포인트 정의 ---
# main.py의 @app 대신 @router 를 사용합니다!

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(task_in: TaskCreate):
    """
    새로운 할 일을 생성합니다.

    - **title**: 할 일 제목 (필수)
    - **description**: 할 일 상세 설명 (선택)
    """
    # (18강에서 구현될 로직 - 지금은 placeholder 또는 간단 응답)
    global next_task_id
    new_task = Task(id=next_task_id, **task_in.model_dump(), completed=False)
    tasks_db[next_task_id] = new_task
    next_task_id += 1
    print(f"Task created: {new_task}")
    return new_task

@router.get("/", response_model=List[Task])
async def read_tasks():
    """
    모든 할 일 목록을 조회합니다.
    """
    # (18강에서 구현될 로직 - 지금은 placeholder)
    print(f"Reading all tasks: {list(tasks_db.values())}")
    return list(tasks_db.values())

@router.get("/{task_id}", response_model=Task)
async def read_task(
    task_id: int = Path(..., title="조회할 Task의 ID", ge=1) # 경로 매개변수 검증 추가 (예시)
):
    """
    주어진 ID에 해당하는 특정 할 일을 조회합니다.
    """
    # (18강에서 구현될 로직 - 지금은 placeholder)
    if task_id not in tasks_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    print(f"Reading task: {tasks_db[task_id]}")
    return tasks_db[task_id]

@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_update: TaskCreate, # 입력 데이터 (TaskCreate 재사용 또는 TaskUpdate 모델 생성)
    task_id: int = Path(..., title="수정할 Task의 ID", ge=1),
):
    """
    주어진 ID에 해당하는 할 일을 수정합니다. (전체 업데이트)
    """
    # (18강에서 구현될 로직 - 지금은 placeholder)
    if task_id not in tasks_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    existing_task = tasks_db[task_id]
    existing_task.title = task_update.title
    existing_task.description = task_update.description
    # completed 상태 업데이트는 별도 엔드포인트(PATCH)나 입력 모델 수정 필요 (추후 고려)
    print(f"Task updated: {existing_task}")
    return existing_task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int = Path(..., title="삭제할 Task의 ID", ge=1)
):
    """
    주어진 ID에 해당하는 할 일을 삭제합니다.
    """
    # (18강에서 구현될 로직 - 지금은 placeholder)
    if task_id not in tasks_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    del tasks_db[task_id]
    print(f"Task deleted: ID={task_id}")
    # 204 응답은 본문이 없으므로 None 반환
    return None

