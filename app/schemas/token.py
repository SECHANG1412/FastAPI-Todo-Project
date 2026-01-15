# app/schemas/token.py (Pydantic 모델)

from pydantic import BaseModel
from typing import Optional


# =========================================================
# 로그인 성공 시 응답용 토큰 스키마
# =========================================================
# OAuth2 표준에 맞춘 로그인 응답 형식
# FastAPI가 자동으로 JSON 응답 검증/문서화에 사용
class Token(BaseModel):
    access_token: str   # 서버가 발급한 JWT 문자열
    token_type: str     # 보통 "bearer"


# =========================================================
# JWT 페이로드 데이터 스키마
# =========================================================
# 토큰 검증 단계에서 JWT 안에 들어 있는 데이터를
# 타입 안전하게 다루기 위해 사용 (30강에서 활용)
class TokenData(BaseModel):
    email: Optional[str] = None     # 토큰에서 추출한 사용자 식별 정보

