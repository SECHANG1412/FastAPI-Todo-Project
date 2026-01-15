# app/routers/users.py
# 사용자(User) 관련 API 엔드포인트를 정의하는 라우터 파일
# 이 파일은 "회원가입(사용자 등록)"이라는 하나의 책임만 가진다

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# =========================================================
# 모델 및 의존성 임포트
# =========================================================
from ..models.user import User as PydanticUser, UserCreate # Pydantic 모델: API 요청(Request)과 응답(Response)의 데이터 형태를 정의
from ..sql_models.user import User as SQLAlchemyUser       # SQLAlchemy 모델: 실제 DB 테이블과 매핑되는 ORM 모델
from ..database import get_db                              # DB 세션 의존성: 요청하마 AsyncSession을 주입받기 위한 함수
from ..security import get_password_hash                   # 비밀번호 해싱 함수: 평문 비밀번호를 안전한 해시값으로 변환



# =========================================================
# 라우터 설정
# =========================================================
# 이 라우터는 main.py 에서
# app.include_router(users.router, prefix="/users", tags=["Users"])
# 같은 방식으로 등록된다.
router = APIRouter()


# =========================================================
# 사용자 등록 API
# =========================================================
@router.post(
        "/", 
        response_model=PydanticUser,            # 응답 시 PydanticUser 모델 형태로 반환
        status_code=status.HTTP_201_CREATED,    # 회원가입 성공 시 201 Created
        summary="Register new user"
)
async def register_user(
    user_in: UserCreate,                        # 요청 본문: email + password
    db: AsyncSession = Depends(get_db)          # DB 세션을 의존성으로 주입
):
    """
    새로운 사용자를 등록합니다.

    처리 흐름:
    1. 이메일 중복 여부 확인
    2. 비밀번호 해싱
    3. 사용자 DB 저장
    4. 생성된 사용자 정보 반환 (비밀번호 제외)
    """

    # =====================================================
    # 1. 이메일 중복 확인
    # =====================================================
    # 동일한 이메일로 여러 계정이 생성되면
    # - 로그인 시 사용자 식별 불가
    # - 보안 및 데이터 무결성 문제 발생
    #
    # 따라서 회원가입 단계에서 반드시 중복 체크 수행
    query = select(SQLAlchemyUser).where(
        SQLAlchemyUser.email == user_in.email
    )

    # AsyncSession.execute():
    # - 비동기 방식으로 SQL 실행
    result = await db.execute(query)

    # scalar_one_or_none():
    # - 결과가 없으면 None
    # - 하나 있으면 해당 객체 반환
    # - 둘 이상이면 예외 (email 은 unique 라는 전제)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        # 이미 존재하는 이메일일 경우 회원가입 거부
        print(f"Registration failed: Email already exists - {user_in.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # =====================================================
    # 2. 비밀번호 해싱
    # =====================================================
    # 절대 평문 비밀번호를 DB에 저장하지 않는다
    #
    # get_password_hash():
    # - bcrypt + salt 를 사용한 단방향 해싱
    # - 서버조차 원래 비밀번호를 알 수 없게 만듦
    hashed_password = get_password_hash(user_in.password)

    # =====================================================
    # 3. SQLAlchemy User 객체 생성
    # =====================================================
    # 여기서 만드는 객체는 "DB에 저장될 사용자"
    # password ❌
    # hashed_password ⭕
    db_user = SQLAlchemyUser(
        email=user_in.email,
        hashed_password=hashed_password
    )

    # =====================================================
    # 4. DB에 사용자 저장
    # =====================================================
    # add(): 세션에 객체 추가
    # commit(): 실제 INSERT 쿼리 실행
    # refresh(): DB에서 최신 상태(id 포함) 다시 불러오기
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    print(f"User registered successfully: {db_user.email} (ID: {db_user.id})")


    # =====================================================
    # 5. 사용자 정보 반환
    # =====================================================
    # 반환값은 SQLAlchemy 객체지만,
    #
    # response_model=PydanticUser 덕분에:
    # - FastAPI가 자동으로 Pydantic 모델로 변환
    # - password / hashed_password 필드는 응답에서 자동 제외
    #
    # 보안상 매우 중요한 포인트
    return db_user