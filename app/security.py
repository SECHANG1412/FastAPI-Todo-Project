# app/security.py

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

