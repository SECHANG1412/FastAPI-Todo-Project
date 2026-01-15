# app/security.py
import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext


# =========================================================
# 비밀번호 해싱 설정 (CryptContext)
# =========================================================
# CryptContext는 "비밀번호 보안 정책 묶음" 이라고 생각하면 된다.
# 여기서 어떤 알고리즘을 쓸지, 어떻게 관리할지를 한 번에 정의한다.
#
# schemes=["bcrypt"]
# - 비밀번호 해싱 알고리즘으로 bcrypt 사용
# - bcrypt는 느리게 동작하도록 설계되어 무차별 대입 공격에 강함
# 
# deprecated="auto"
# - 예전에 사용하던 해싱 방식이 있다면 자동으로 감지
# - 로그인 시 더 최신 알고리즘으로 재해싱 가능
# - 지금 단계에서는 깊이 이해하지 않아도 되지만, 실무에선 매우 중요
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto"
)


# =========================================================
# 비밀번호 검증 함수
# =========================================================
# 사용자가 로그인할 때 입력한 비밀번호(plain_password)와 
# DB에 저장된 해시 비밀번호(hashed_password)가
# 같은 비밀번호인지 확인하는 함수
#
# 중요 포인트
# - 절대 "해시를 복호화" 하지 않는다 (불가능)
# - 입력된 평문 비밀번호를 같은 방식으로 해싱한 뒤 비교한다
# - passlib이 내부적으로 salt, 알고리즘, 옵션까지 자동 처리
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    plain_password : 사용자가 로그인 시 입력한 비밀번호 (평문)
    hashed_password: DB에 저장된 해시된 비밀번호

    반환값:
    - True  -> 비밀번호 일치 (로그인 성공 가능)
    - False -> 비밀번호 불일치
    """
    return pwd_context.verify(plain_password, hashed_password)


# =========================================================
# 비밀번호 해싱 함수
# =========================================================
# 회원가입 시 사용되는 함수
# 사용자가 입력한 평문 비밀번호를
# bcrypt + salt를 적용해 안전한 해시값으로 변환한다
#
# 매우 중요
# - 이 함수의 결과만 DB에 저장한다
# - 평문 비밀번호는 절대 DB에 저장하지 않는다
# - 서버도 사용자의 원래 비밀번호를 알 수 없게 만드는 것이 목표
def get_password_hash(password: str) -> str:
    """
    password: 사용자가 회원가입 시 입력한 평문 비밀번호

    반환값:
    - bcrypt로 해싱된 문자열
      (예: $2b$12$QpE3....)
    """
    return pwd_context.hash(password)



# JWT 서명에 사용할 비밀 키
# 실무에서는 반드시 환경 변수로 관리해야 함
SECRET_KEY = os.getenv("SECRET_KEY", "a_very_secret_key_that_should_be_in_env_var_or_secret_manager_0123456789abcdef")

# JWT 서명 알고리즘 (대칭키 방식)
ALGORITHM = "HS256"

# Access Token 만료 시간 (분 단위)
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# OAuth2 Bearer 토큰 추출 설정
# Authorization: Bearer <token> 헤더에서 토큰을 꺼내주는 역할
# tokenUrl은 Swagger 문서용 (실제 호출 X)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# JWT Access Token 생성 함수
# 로그인 성공 시 호출되어 JWT를 생성/서명한다
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:

    # JWT payload로 사용할 데이터 복사 (원본 dict 보호)
    to_encode = data.copy()

    # 만료 시간이 외부에서 전달된 경우
    if expires_delta:
        # 현재 UTC 시간 기준으로 만료 시간 계산
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # 전달되지 않았다면 기본 만료 시간(ACCESS_TOKEN_EXPIRE_MINUTES) 사용
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # JWT 표준 클레임인 exp(만료 시간)를 payload에 추가
    to_encode.update({"exp": expire})

    # payload를 SECRET_KEY로 서명하여 JWT 문자열 생성
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # 완성된 JWT(access token) 반환
    return encoded_jwt
