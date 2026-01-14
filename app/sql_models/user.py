from sqlalchemy import String, Integer, Column
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List, Optional
from ..database import Base


# User 클래스 정의
# 이 클래스 하나가 DB의 users 테이블과 1:1로 연결된다
class User(Base):
    # 이 클래스가 연결된 실제 DB 테이블 이름
    __tablename__ = "users"


    # id 컬럼 정의
    # - 정수(Integer) 타입
    # - primary_key=True : 이 컬럼이 테이블의 대표 번호(PK)
    # - index=True : 조회 속도를 빠르게 하기 위한 인덱스 생성
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # email 컬럼 정의
    # - 최대 길이 100자인 문자열
    # - unique=True : 이메일은 중복되면 안 됨 (한 사람당 하나)
    # - index=True : 이메일로 자주 조회할 수 있으니 인덱스 생성
    # - nullable=False : 반드시 값이 있어야 함 (비어 있으면 안 됨)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)

    # hashed_password 컬럼 정의
    # - 실제 비밀번호 ❌
    # - 암호화된 비밀번호를 저장
    # - nullable=True : 아직 인증을 본격적으로 안 쓰는 단계라 비어 있어도 허용
    hashed_password: Mapped[str] = mapped_column(String, nullable=True)

    # tasks 속성 정의 (⚠️ 이건 DB 컬럼이 아님!)
    # - 이 User가 가지고 있는 Task 목록
    # - List["Task"] : Task 객체 여러 개를 리스트로 가진다는 뜻
    # - relationship("Task") : Task 모델과 연결
    # - back_populates="owner" : Task 모델에 있는 owner 속성과 서로 연결됨을 약속
    # 즉,
    # user.tasks → 이 사람이 가진 모든 할 일
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="owner")



    # 객체를 print() 했을 때 보기 좋게 출력해 주는 함수
    # 디버깅할 때 유용
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"