# app/security.py
import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .database import get_db
from .sql_models.user import User as SQLAlchemyUser

from .schemas.token import TokenData



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


#################################################################################################################################


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

#################################################################################################################################

# =========================================================
# 현재 사용자 가져오기 의존성 함수
# =========================================================

# 이 함수는 "인증이 필요한 모든 API의 문지기" 역할을 한다.
# - JWT 토큰을 검사하고
# - 토큰의 주인이 실제 DB에 존재하는 사용자면
# - 그 사용자(SQLAlchemy User 객체)를 반환한다
#
# 이 함수가 실패하면:
# → API 로직은 실행되지 않고
# → 즉시 401 Unauthorized 응답이 반환된다
#
# 즉, Depends(get_current_user)가 붙은 API는
# "로그인한 사용자만 접근 가능" 상태가 된다.

async def get_current_user(
    token: str = Depends(oauth2_scheme),    # Authorization: Bearer 헤더에서 JWT 토큰 문자열만 자동으로 추출
    db: AsyncSession = Depends(get_db)      # DB 세션 주입 → FastAPI가 요청마다 새로운 AsyncSession을 만들어 전달
) -> SQLAlchemyUser:
    
    """
    JWT 토큰을 검증하고 현재 로그인된 사용자를 반환하는 의존성 함수.

    성공:
    - SQLAlchemy User 객체 반환
    
    실패:
    - HTTP 401 Unauthorized 발생
    """

    # -----------------------------------------------------
    # 인증 실패 시 공통으로 사용할 예외 객체
    # -----------------------------------------------------
    # - 토큰이 없거나
    # - 토큰이 위조되었거나
    # - 토큰이 만료되었거나
    # - 토큰의 사용자 정보가 잘못되었거나
    # - DB에 해당 사용자가 존재하지 않으면
    #
    # 전부 이 예외로 처리한다
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # -------------------------------------------------
        # 1. JWT 디코딩 + 검증
        # -------------------------------------------------
        # 이 한 줄에서 동시에 일어나는 것:
        # - JWT 서명 검증 (SECRET_KEY)
        # - 알고리즘 검증 (HS256)
        # - exp(만료 시간) 자동 검사
        #
        # 하나라도 실패하면 JWTError 발생
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # -------------------------------------------------
        # 2. JWT payload에서 사용자 식별자 추출
        # -------------------------------------------------
        # JWT 표준 관례:
        # - sub(subject) 클레임에 "토큰의 주인"을 넣는다
        # - 여기서는 email을 사용
        email: str = payload.get("sub")

        # sub 클레임이 없으면 → 구조가 잘못된 토큰
        if email is None:
            print("JWT 'sub' claim missing")
            raise credentials_exception
        
        # -------------------------------------------------
        # 3. (선택) 토큰 데이터 구조 검증
        # -------------------------------------------------
        # Pydantic 모델을 사용해
        # 토큰 데이터 형식을 명확히 한다
        token_data = TokenData(email=email)
    


    except JWTError as e:
        # -------------------------------------------------
        # JWT 검증 실패
        # -------------------------------------------------
        # - 위조된 토큰
        # - 만료된 토큰
        # - 잘못된 형식의 토큰
        #
        # 전부 여기로 떨어진다
        print(f"JWT Error during decoding: {e}")
        raise credentials_exception
    



    # -----------------------------------------------------
    # 4. DB에서 사용자 조회
    # -----------------------------------------------------
    # 토큰은 유효해도,
    # 실제 DB에 사용자가 없을 수 있다
    # (탈퇴, 삭제, 비활성화 등)
    query = select(SQLAlchemyUser).where(
        SQLAlchemyUser.email == token_data.email
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()


    # -----------------------------------------------------
    # 5. 사용자가 DB에 없으면 인증 실패
    # -----------------------------------------------------
    if user is None:
        print(f"User not found in DB for email from token: {token_data.email}")
        raise credentials_exception
    

    # -----------------------------------------------------
    # 6. 인증 성공
    # -----------------------------------------------------
    # 이제 이 반환값이
    # API 함수의 current_user 파라미터로 주입된다
    return user