# app/sql_models/task.py

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional
from ..database import Base


# Task 클래스는 "tasks 테이블의 설계도"이다
# Base를 상속받았기 때문에 ORM 모델이 된다
class Task(Base):

    # 실제 데이터베이스에서 사용할 테이블 이름
    __tablename__ = "tasks"   
    

    # id 컬럼
    # Mapped[int]       : 이 변수는 int 타입의 DB 컬럼이다
    # Integer           : 숫자로 저장
    # primary_key=True  : 이 테이블에서 가장 중요한 대표 번호
    # index=True        : 빠르게 찾을 수 있도록 색인 생성
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    

    # title 컬럼
    # String(100)       : 최대 100글자까지 저장 가능
    # index=True        : 제목으로 검색할 일이 많으니까 빠르게 찾도록 설정
    title: Mapped[str] = mapped_column(String(100), index=True)
    

    # description 컬럼
    # Optional[str]     : 값이 없어도 되는 글자
    # String(500)       : 최대 500글자까지 저장
    # nullable=True     : 비어 있어도 OK
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    
    # completed 컬럼
    # Boolean           : 참(True) / 거짓(False) 값
    # default=False     : 파이썬에서 기본값은 False
    # server_default    : DB에서도 기본값을 False로 설정
    completed: Mapped[bool] = mapped_column(Boolean, default=False, server_default='false')



    # --- ✨ User(사용자)와의 관계를 위한 부분 ✨ ---

    # owner_id 컬럼
    # 실제 데이터베이스(DB)에 저장되는 값
    # "이 할 일(Task)의 주인이 누구인지"를 숫자로 저장
    # ForeignKey("users.id"):
    #    → users 테이블의 id 값을 참조한다는 뜻
    #    → 즉, 존재하는 사용자(id)만 주인이 될 수 있음
    # Optional[int]:
    #    → 아직 주인이 없는 할 일도 허용 (None 가능)
    # nullable=True:
    #    → DB에서도 NULL 허용
    owner_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)


    # owner 관계(relationship)
    # 이 컬럼은 DB에 실제로 저장되지 않는다 ❌
    # 파이썬 코드에서만 사용하는 "객체 연결용 통로"
    # task.owner 를 통해
    #    → 이 할 일의 주인(User 객체)에 바로 접근 가능
    # relationship("User"):
    #    → User 모델과 연결한다는 뜻
    # back_populates="tasks":
    #    → User 모델의 user.tasks 와 서로 연결됨
    #    → (user.tasks <-> task.owner) 양방향 관계 완성
    owner: Mapped["User"] = relationship("User", back_populates="tasks")
    
    # -----------------------------------------------


    # 객체를 print 했을 때 보기 좋게 출력해주는 함수
    # 개발자가 디버깅할 때 편하게 보려고 만드는 것
    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', completed={self.completed})>"