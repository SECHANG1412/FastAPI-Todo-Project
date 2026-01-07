# app/models/task.py
from pydantic import BaseModel, Field
from typing import Optional

# 공통 필드를 위한 기본 모델
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="할 일 제목 (1~100자)")
    description: Optional[str] = Field(default=None, max_length=500, description="상세 설명 (최대 500자)")

    model_config = { # Pydantic V2 설정
        "json_schema_extra": {
            "examples": [ {"title": "장보기", "description": "우유, 계란, 파 사기"} ]
        }
    }

# 할 일 생성 시 요청 본문 모델
class TaskCreate(TaskBase):
    pass

# 할 일 응답 또는 내부 표현 모델
class Task(TaskBase):
    id: int = Field(..., description="고유 Task ID")
    completed: bool = Field(default=False, description="완료 여부")

    model_config = { # Pydantic V2 설정
        "json_schema_extra": {
            "examples": [
                { "id": 1, "title": "FastAPI 공부하기", "description": "17강 프로젝트 구조화 완료하기", "completed": False }
            ]
        }
    }
