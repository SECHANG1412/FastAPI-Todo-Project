# app/routers/tasks.py

from fastapi import APIRouter, HTTPException, status, Path, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Pydantic 모델과 SQLAlchemy 모델 임포트
from ..models.task import Task as PydanticTask, TaskCreate  # Pydantic 모델 (이름 충돌 피하기 위해 alias 사용)
from ..sql_models.task import Task as SQLAlchemyTask        # SQLAlchemy 모델 (이름 충돌 피하기 위해 alias 사용)

# 데이터베이스 세션 의존성 임포트
from ..database import get_db


router = APIRouter()


# --- ORM을 사용한 Task CRUD 구현 ----

# 1. Create Task (할 일 생성)
@router.post(
        "/", 
        response_model=PydanticTask,            # 응답 데이터는 PydanticTask 모양
        status_code=status.HTTP_201_CREATED,    # 성공 시 201 Created
        summary="Create a new task"
)
async def create_task(
    task_in: TaskCreate,                        # 클라이언트가 보낸 데이터 (Pydantic 모델)
    db: AsyncSession = Depends(get_db)          # DB 세션을 get_db로부터 주입받음
):
    """
    새로운 할 일을 생성하고 데이터베이스에 저장합니다.
    """
    # 1. Pydantic 모델(TaskCreate)을 SQLAlchemy 모델 객체로 변환
    # **dict 형태로 바꿔서(**) SQLAlchemyTask 생성자에 전달
    db_task = SQLAlchemyTask(**task_in.model_dump())    

    # 2. 이 객체를 세션에 등록 → 아직 DB에 저장된 건 아니고, "저장 예정" 상태
    db.add(db_task)                                     

    # 3. commit → 실제로 INSERT SQL이 실행되어 DB에 영구 저장됨
    await db.commit()         

    # 4. refresh → DB가 자동으로 만든 값(id 같은 것)을 다시 객체에 채워 넣음               
    await db.refresh(db_task)                          
    print(f"Task created in DB: {db_task}")

    # 5. SQLAlchemy 객체 반환 → FastAPI가 response_model(PydanticTask)에 맞게 자동 변환
    return db_task 



# 2. Read Tasks (할 일 목록 조회)
@router.get(
        "/", 
        response_model=List[PydanticTask], # 여러 개의 Task를 리스트로 변환
        summary="Get all tasks"
)
async def read_tasks(
    skip: int = 0,                          # 몇 개를 건너뛸지 (페이징용)
    limit: int = 100,                       # 최대 몇 개까지 가져올지
    db: AsyncSession = Depends(get_db)      # DB 세션 주입
):
    """
    모든 할 일 목록을 데이터베이스에서 조회합니다. (페이징 가능)
    """
    # 1. SQL 쿼리 만들기 → SELECT * FROM tasks OFFSET skip LIMIT limit
    query = select(SQLAlchemyTask).offset(skip).limit(limit)

    # 2. 쿼리 실행
    result = await db.execute(query)

    # 3. 결과에서 SQLAlchemyTask 객체만 뽑아서 리스트로 만들기
    tasks = result.scalars().all()
    print(f"Reading all tasks (limit={limit}, skip={skip}) - Found {len(tasks)} items")

    # 4. 결과 반환 (자동으로 Pydantic 모델 리스트로 변환됨)
    return tasks



# 3. Read Task (할 일 하나 조회)
@router.get(
        "/{task_id}", 
        response_model=PydanticTask, 
        summary="Get a specific task by ID"
)
async def read_task(
    task_id: int = Path(..., title="The ID of the task to get", ge=1),  # task_id는 1 이상
    db: AsyncSession = Depends(get_db)
):
    """
    주어진 ID에 해당하는 특정 할 일을 데이터베이스에서 조회합니다.
    """
    # 1. Primary Key(id)로 Task 하나 조회
    task = await db.get(SQLAlchemyTask, task_id)

    # 2. 없으면 404 에러
    if task is None:
        print(f"Task not found in DB for ID: {task_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    print(f"Reading task from DB: {task}")

    # 3. 조회된 Task 반환
    return task


# 4. Update Task (할 일 수정)
@router.put("/{task_id}", response_model=PydanticTask, summary="Update a task")
async def update_task(
    task_update: TaskCreate,
    task_id: int = Path(..., title="The ID of the task to update", ge=1),
    db: AsyncSession = Depends(get_db)
):
    """
    주어진 ID에 해당하는 할 일을 데이터베이스에서 수정합니다.
    """
    # 1. 수정할 Task 객체 조회 
    db_task = await db.get(SQLAlchemyTask, task_id)

    # 없으면 404
    if db_task is None:
        print(f"Task not found for update: ID={task_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    
    # 2. 클라이언트가 보낸 데이터만 꺼내기
    # exclude_unset=True → 보내기 않은 필드는 건드리지 않음
    update_data = task_update.model_dump(exclude_unset=True)

    # 3. SQLAlchemy 객체의 속성 직접 수정
    for key, value in update_data.items():
        setattr(db_task, key, value)
    
        # ⚠️ 여기서 db.add(db_task)는 사실 한 번만 해도 됨
        # SQLAlchemy는 이미 객체 변경을 자동으로 감지함 
        db.add(db_task)

    # 5. 변경사항 커밋 → 실제 UPDATE 실행
    await db.commit()

    # 5. 변경된 객체 상태 DB와 동기화 (선택적이지만 권장)
    await db.refresh(db_task)
    print(f"Task updated in DB: {db_task}")

    # 6. 수정된 SQLAlchemyTask 객체 반환 (response_model 적용)
    return db_task



# 5. Delete Task (할 일 삭제)
@router.delete(
        "/{task_id}", 
        status_code=status.HTTP_204_NO_CONTENT,  # 성공 시 204 (본문 없음)
        summary="Delete a task"
)
async def delete_task(
    task_id: int = Path(..., title="The ID of the task to delete", ge=1),
    db: AsyncSession = Depends(get_db)
):
    """
    주어진 ID에 해당하는 할 일을 데이터베이스에서 삭제합니다.
    """
    # 1. 삭제할 Task 객체 조회
    db_task = await db.get(SQLAlchemyTask, task_id)

    # 없으면 404
    if db_task is None:
        print(f"Task not found for deletion: ID={task_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    
    # 2. 세션에서 객체 삭제 요청 (아직 DB 반영 안됨)
    await db.delete(db_task)

    # 3. 변경사항 커밋 → 실제 DELETE 실행
    await db.commit()
    print(f"Task deleted from DB: ID={task_id}")

    # 4. 204 응답은 본문 없음
    return None