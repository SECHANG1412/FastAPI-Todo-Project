# app/models/task.py

from pydantic import BaseModel, Field   # pydantic에서 제공하는 BaseModel을 가져온다 → "데이터 규칙을 만들기 위한 기본 재료"
from typing import Optional             # Optional은 "있어도 되고, 없어도 되는 값"이라는 뜻


# Task의 가장 기본이 되는 공통 설계도 → "할 일이라면 최소한 이런 모양을 가져야 해"
class TaskBase(BaseModel):
    
    title: str = Field(..., min_length=1, max_length=100, description="할 일 제목 (1~100자)")
    # title은 문자열(str)이고 반드시 있어야 한다.
    # Field(...)에서 ...은 "이 값은 필수!"라는 뜻
    # min_length=1 → 최소 1글자 이상
    # max_length=100 → 최대 100글자까지
    # description → API 문서에 설명으로 보여짐

    description: Optional[str] = Field(default=None, max_length=500, description="상세 설명 (최대 500자)")
    # description은 문자열이거나(None 가능)
    # Optional[str] → 있어도 되고 없어도 됨
    # default=None → 안 보내면 자동으로 None
    # max_length=500 → 최대 500글자
    

    # "예시 데이터"
    # Swagger(API 설명서)에 예제로 보여짐
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "장보기",                      # 할 일 제목 예시
                    "description": "우유, 계란, 파 사기"    # 할 일 설명 예시
                    }
            ]
        }
    }



# Task를 "새로 만들 때" 사용하는 설계도
# TaskBase를 그대로 물려받는다
class TaskCreate(TaskBase):
    pass
    # pass는 "추가할 건 없어요"라는 뜻 → TaskBase랑 똑같은 규칙 사용



# 실제로 저장되었거나, 조회해서 보여줄 때 사용하는 설계도
class Task(TaskBase):

    id: int = Field(..., description="고유 Task ID")                    # id는 숫자(int)이고 반드시 있어야 한다 → 서버가 자동으로 붙여주는 번호
    completed: bool = Field(default=False, description="완료 여부")     # completed는 True 또는 False, default=False → 처음 만들면 자동으로 False

    # 이 Task의 예시 데이터
    # 조회 결과 예시로 Swagger에 표시됨
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1, 
                    "title": "FastAPI 공부하기", 
                    "description": "17강 프로젝트 구조화 완료하기", 
                    "completed": False
                }
            ]
        }
    }