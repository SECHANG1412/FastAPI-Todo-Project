# app/models/user.py (Pydantic 모델)
# 사용자(User)와 관련된 Pydantic 모델 정의 파일
# 이 파일은 "요청(Request)과 응답(Response)의 데이터 형태"만 책임진다
# DB(SQLAlchemy) 모델과는 역할이 다르다는 점이 중요하다

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# =========================================================
# 공통 사용자 속성 (Base Model)
# =========================================================
# UserBase는 "사용자라면 공통으로 가지는 필드"
# 여러 모델에서 재사용하기 위한 부모 클래스 역할
#
#   아직 password는 포함하지 않는다 
#   (비밀번호는 오직 생성/로그인 시에만 필요하기 때문)
class UserBase(BaseModel):
    # EmailStr:
    # - Pydantic이 제공하는 이메일 전용 타입
    # - 문자열이지만, 이메일 형식이 아니면 자동으로 validation 에러 발생
    email: EmailStr = Field(
        ..., 
        examples=["john.doe@example.com"]
    )


# =========================================================
# 사용자 생성 요청 모델 (회원가입용)
# =========================================================
# POST /users/ 요청에서 사용되는 입력 모델
# "회원가입 시 클라이언트가 보내야 하는 데이터 구조"를 정의한다.
#
# ✔ 비밀번호 포함
# ❌ DB 모델 아님
# ❌ 응답 모델 아님
class UserCreate(UserBase):
    # password:
    # - 회원가입 시에만 필요한 필드
    # - min_length=8 로 최소 길이 검증을 Pydantic 레벨에서 수행
    # - 이 단계에서는 아직 '해싱'이 적용되지 않은 평문 비밀번호
    password: str = Field(
        ..., 
        min_length=8, 
        description="비밀번호는 최소 8자 이상이어야 합니다."
    )


# =========================================================
# 사용자 정보 응답 모델 (비밀번호 제외)
# =========================================================
# API 응답(Response)으로 클라이언트에게 내려줄 사용자 정보 모델
#
# 매우 중요
# - password 필드는 절대 포함하지 않는다
# - 해시된 비밀번호조차도 응답으로 보내지 않는다
#
# 이 모델은:
# - 회원가입 성공 응답
# - 사용자 조회 응답
# 등에 사용된다.
class User(BaseModel):
    # id:
    # - DB에 저장된 사용자 고유 ID
    # - 클라이언트가 사용자를 식별할 때 사용
    id: int

    # model_config:
    # from_attributes=True 는
    # SQLAlchemy ORM 객체 → Pydantic 모델 변환을 허용하는 설정
    #
    # 즉, 아래 같은 코드가 가능해진다:
    #   return User.model_validate(db_user)
    model_config = {"from_attributes": True}    