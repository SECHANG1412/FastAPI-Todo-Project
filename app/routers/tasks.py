# app/routers/tasks.py

from fastapi import APIRouter, HTTPException, status, Path
from typing import List, Dict
from ..models.task import Task, TaskCreate


router = APIRouter()                # APIRouter 객체를 하나 만든다 → 이 파일 전체가 하나의 API 묶음이 됨


tasks_db: Dict[int, Task] = {}      # 실제 DB 대신 쓰는 가짜 데이터 저장소 → Key: task_id, value: Task 객체
next_task_id: int = 1               # 다음에 만들 Task에 붙일 번호 → Task 하나 만들 때마다 1씩 증가



# POST 요청: 새 할 일 만들기
@router.post(
        "/",                                    # "/" → /tasks/
        response_model=Task,                    # response_model=Task → 응답은 Task 모양으로 돌려줌
        status_code=status.HTTP_201_CREATED,    # status_code=201 → "성공적으로 생성됨"이라는 뜻
        summary="Create a new task"
)
async def create_task(
    task_in: TaskCreate                 # 사용자가 보내는 데이터 → title, description 규칙을 반드시 만족해야 함
):
    global next_task_id                 # 함수 안에서 전역 변수 next_task_id를 사용하겠다고 선언

    # 새 Task 객체 생성
    new_task = Task(
        id=next_task_id,                # 서버가 자동으로 번호를 붙여줌 
        **task_in.model_dump()          # title, description을 꺼내서 넣음
    )

    tasks_db[next_task_id] = new_task   # 만든 Task를 가짜 DB(딕셔너리)에 저장
    next_task_id += 1                   # 다음 Task를 위해 번호 1 증가
    print(f"Task created: {new_task}")  # 콘솔에 로그 출력 (개발자가 확인용)
    return new_task                     # 만든 Task를 사용자에게 반환



# GET 요청: 모든 할 일 조회
@router.get(
        "/",                        # "/" → /tasks/
        response_model=List[Task],  # response_model=List[Task] → Task 여러 개를 리스트로 반환
        summary="Get all tasks"    
)
async def read_tasks():
    print(f"Reading all tasks ({len(tasks_db)} items)") # 현재 몇 개의 Task가 있는지 콘솔에 출력
    return list(tasks_db.values())                      # 딕셔너리에 저장된 Task들을 리스트로 바꿔서 반환




# GET 요청: 특정 할 일 하나 조회
@router.get(
        "/{task_id}",                           # "/{task_id}" → /tasks/{task_id}
        response_model=Task,                    
        summary="Get a specific task by ID"
)
async def read_task(
    # task_id → URL 경로에서 받아오는 번호
    task_id: int = Path(                        
        ...,                                    # Path(...) → 반드시 있어야 함
        title="The ID of the task to get",      # title → API 문서에 표시될 설명
        ge=1                                    # ge=1 → 1 이상만 허용
    )
):
    task = tasks_db.get(task_id)                # 딕셔너리에서 해당 ID의 Task를 가져옴

    # 만약 해당 ID의 Task가 없다면
    if task is None:
        print(f"Task not found for ID: {task_id}")

        # 일부러 404 에러 발생
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    
    print(f"Reading task: {task}")  # 정상적으로 찾았으면 콘솔에 출력
    return task                     # 해당 Task 반환




# PUT 요청: 기존 할 일 수정
@router.put(
        "/{task_id}",               # "/{task_id}" → /tasks/{task_id}
        response_model=Task, 
        summary="Update a task"
)
async def update_task(
    task_update: TaskCreate,        # 수정할 내용 (title, description)

    # 수정할 대상의 ID
    task_id: int = Path(    
        ..., 
        title="The ID of the task to update", 
        ge=1
    )
):
    task = tasks_db.get(task_id)    # 해당 ID의 Task 가져오기

    # 만약 Task가 없다면
    if task is None:
        print(f"Task not found for update: ID={task_id}")

        # 404 에러 발생
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    
    task.title = task_update.title              # 기존 Task의 제목 수정
    task.description = task_update.description  # 기존 Task의 설명 수정

    print(f"Task updated: {task}")              # 수정 완료 로그 출력
    return task                                 # 수정된 Task 반환



# DELETE 요청: 할 일 삭제
@router.delete(
        "/{task_id}",                               # "/{task_id}" → /tasks/{task_id}
        status_code=status.HTTP_204_NO_CONTENT,     # 성공 시 204 → 응답 본문 없음
        summary="Delete a task"
)
async def delete_task(
    # 삭제할 Task의 ID
    task_id: int = Path(
        ..., 
        title="The ID of the task to delete", 
        ge=1
    )
):
    # 만약 해당 ID가 없다면
    if task_id not in tasks_db:
        print(f"Task not found for deletion: ID={task_id}")

        # 404 에러 발생
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    
    del tasks_db[task_id]                   # 딕셔너리에서 해당 Task 삭제

    print(f"Task deleted: ID={task_id}")    # 삭제 로그 출력
    return None                             # 204 응답은 돌려줄 데이터가 없으므로 None 반환