# app/routers/tasks.py

from fastapi import APIRouter, HTTPException, status, Path, Depends 
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.task import Task as PydanticTask, TaskCreate
from ..sql_models.task import Task as SQLAlchemyTask
from ..sql_models.user import User as SQLAlchemyUser
from ..database import get_db
from ..security import get_current_user


# ---------------------------------------------------------
# Task 관련 API 라우터
# ---------------------------------------------------------
router = APIRouter()



# =========================================================
# Task 생성 API
# =========================================================

@router.post(
    "/",
    response_model=PydanticTask,                        # 응답은 Pydantic Task 형태
    status_code=status.HTTP_201_CREATED,                # 생성 성공 시 201
    summary="Create a new task for the current user"
)
async def create_task(
    task_in: TaskCreate,                                        # 클라이언트가 전달한 Task 생성 데이터
    db: AsyncSession = Depends(get_db),                         # DB 세션 주입
    current_user: SQLAlchemyUser = Depends(get_current_user)    # 현재 로그인한 사용자 주입 - JWT 검증 실패 시 이 함수는 실행되지 않음
):
    # SQLAlchemy Task 객체 생성
    # **중요**
    # - owner_id를 현재 로그인한 사용자 ID로 설정
    # - 클라이언트가 owner_id를 조작할 수 없도록 서버에서 직접 설정
    db_task = SQLAlchemyTask(
        **task_in.model_dump(),
        owner_id=current_user.id
    )

    
    db.add(db_task)             # DB에 추가
    await db.commit()           # INSERT 쿼리 실행
    await db.refresh(db_task)   # DB에서 최신 상태 다시 로드

    print(f"User '{current_user.email}' created task: {db_task.title}")

    return db_task    



# =========================================================
# Task 목록 조회 API
# =========================================================
@router.get(
    "/",
    response_model=List[PydanticTask],             # Task 리스트 반환
    summary="Get tasks for the current user"
)
async def read_tasks(
    db: AsyncSession = Depends(get_db),                          # DB 세션 주입
    current_user: SQLAlchemyUser = Depends(get_current_user),       # 현재 로그인한 사용자 주입

    # 페이징 옵션
    skip: int = 0,
    limit: int = 100
):
    # 현재 로그인한 사용자의 Task만 조회
    # - owner_id 조건 필수
    query = (
        select(SQLAlchemyTask)
        .where(SQLAlchemyTask.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)    # 쿼리 실행
    tasks = result.scalars().all()      # 결과를 리스트로 변환

    print(f"User '{current_user.email}' reading their tasks ({len(tasks)} items)")

    return tasks                    




# =========================================================
# 특정 Task 단건 조회 API
# =========================================================
@router.get(
    "/{task_id}",
    response_model=PydanticTask,
    summary="Get a specific task by ID for the current user"
)
async def read_task(
    task_id: int = Path(..., ge=1),                             # URL 경로에서 task_id 추출 (1 이상의 정수만 허용)
    db: AsyncSession = Depends(get_db),                         # DB 세션 주입
    current_user: SQLAlchemyUser = Depends(get_current_user)    # 현재 로그인한 사용자 주입
):
    # 특정 task_id + 현재 사용자 소유(owner_id) 조건으로 조회
    # → 남의 Task 접근 차단
    query = select(SQLAlchemyTask).where(
        SQLAlchemyTask.id == task_id,
        SQLAlchemyTask.owner_id == current_user.id
    )

    # 쿼리 실행
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    # Task가 없으면 (존재하지 않거나, 남의 Task)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    print(f"User '{current_user.email}' reading task ID: {task_id}")

    return task






# =========================================================
# Task 수정 API
# =========================================================
@router.put(
    "/{task_id}",
    response_model=PydanticTask,
    summary="Update a task for the current user"
)
async def update_task(
    task_update: TaskCreate,                                    # 수정할 Task 데이터
    task_id: int = Path(..., ge=1),                             # URL 경로 파라미터
    db: AsyncSession = Depends(get_db),                         # DB 세션 주입
    current_user: SQLAlchemyUser = Depends(get_current_user)    # 현재 로그인한 사용자 주입
):
    # 수정 대상 Task 조회 (ID + owner_id 조건)
    query = select(SQLAlchemyTask).where(
        SQLAlchemyTask.id == task_id,
        SQLAlchemyTask.owner_id == current_user.id
    )
    result = await db.execute(query)
    db_task = result.scalar_one_or_none()

    # Task가 없으면 404
    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # 전달된 데이터 중 실제로 값이 있는 필드만 추출
    update_data = task_update.model_dump(exclude_unset=True)

    # 기존 Task 객체에 값 반영
    for key, value in update_data.items():
        setattr(db_task, key, value)

    await db.commit()           # 변경 사항 저장
    await db.refresh(db_task)   # 최신 상태 다시 로드

    print(f"User '{current_user.email}' updated task ID: {task_id}")

    return db_task




# =========================================================
# Task 삭제 API
# =========================================================
@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task for the current user"
)
async def delete_task(
    task_id: int = Path(..., ge=1),                             # 삭제할 Task ID
    db: AsyncSession = Depends(get_db),                         # DB 세션 주입
    current_user: SQLAlchemyUser = Depends(get_current_user)    # 현재 로그인한 사용자 주입
):
    # 삭제 대상 Task 조회 (ID + owner_id 조건)
    query = select(SQLAlchemyTask).where(
        SQLAlchemyTask.id == task_id,
        SQLAlchemyTask.owner_id == current_user.id
    )
    result = await db.execute(query)
    db_task = result.scalar_one_or_none()

    # Task가 없으면 404
    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    await db.delete(db_task)    # Task 삭제
    await db.commit()           # DELETE 쿼리 실행

    print(f"User '{current_user.email}' deleted task ID: {task_id}")

    return None # 204 No Content → 반환값 없음
