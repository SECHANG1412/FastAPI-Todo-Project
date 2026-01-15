# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..database import get_db
from ..sql_models.user import User as SQLAlchemyUser
from ..schemas.token import Token
from ..security import verify_password, create_access_token 


# ---------------------------------------------------------
# 인증(Auth) 관련 라우터 생성
# ---------------------------------------------------------
# 이 라우터에 정의된 모든 엔드포인트는
# main.py에서 include_router로 등록되어 실제 API가 됨
router = APIRouter()



# ---------------------------------------------------------
# 로그인 + Access Token 발급 엔드포인트
# ---------------------------------------------------------
# POST /token 요청을 받아 로그인 처리 후 JWT를 발급
# OAuth2 표준에서 "토큰 발급 엔드포인트" 역할
@router.post(
        "/token", 
        response_model=Token,        # 응답 형식을 Token 스키마로 제한
        summary="Get access token"   # Swagger 문서에 표시될 설명
)
async def login_for_access_token(
    # OAuth2PasswordRequestForm을 통해
    # form-data 형식의 username / password 자동 주입
    form_data: OAuth2PasswordRequestForm = Depends(), 
    # 비동기 DB 세션 주입
    db: AsyncSession = Depends(get_db)
):
    """
    사용자 이메일(폼 데이터의 'username' 필드)과 비밀번호를 사용하여 인증하고,
    성공 시 JWT 액세스 토큰을 반환합니다.
    """
    # -----------------------------------------------------
    # 1. 사용자 조회
    # -----------------------------------------------------
    # OAuth2 표준에서는 필드명이 username 이지만, 이 프로젝트에서는 email을 username으로 사용
    query = select(SQLAlchemyUser).where(SQLAlchemyUser.email == form_data.username)
    result = await db.execute(query)    # 쿼리 실행
    user = result.scalar_one_or_none()  # 결과에서 User 객체 하나 또는 None 추출



    # -----------------------------------------------------
    # 2. 인증 실패 처리
    # -----------------------------------------------------
    # - 사용자가 존재하지 않거나
    # - 비밀번호가 일치하지 않는 경우
    if not user or not verify_password(form_data.password, user.hashed_password):

        # 보안 로그용 출력 (실무에서는 logger 사용)
        print(f"Login failed for email: {form_data.username}")

        # 인증 실패 → 401 Unauthorized
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",       # 어떤 쪽이 틀렸는지 알려주지 않음 (보안상 중요)
            headers={"WWW-Authenticate": "Bearer"},     # OAuth2 / Bearer 인증을 사용한다는 것을 명시
        )



    # -----------------------------------------------------
    # 3. JWT Payload 구성
    # -----------------------------------------------------
    # JWT 안에 들어갈 데이터
    # sub(subject)는 "이 토큰의 주체가 누구인가"를 의미
    # 보통 user_id 또는 email을 사용
    access_token_data = {
        "sub": user.email
    }



    # -----------------------------------------------------
    # 4. JWT Access Token 생성
    # -----------------------------------------------------
    # security.py에 정의된 create_access_token 함수 호출
    # 내부에서 만료 시간(exp)과 서명이 자동으로 처리됨
    access_token = create_access_token(
        data=access_token_data
    )


    # 로그인 성공 로그
    print(f"User {user.email} logged in successfully.")


    # -----------------------------------------------------
    # 5. 토큰 응답 반환
    # -----------------------------------------------------
    # OAuth2 표준 형식:
    # {
    #   "access_token": "...",
    #   "token_type": "bearer"
    # }
    #
    # response_model=Token 설정 덕분에
    # FastAPI가 자동으로 검증 및 직렬화 수행
    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }