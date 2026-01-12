# app/sql_models/task.py

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional
from ..database import Base


# Task 클래스는 "tasks 테이블의 설계도"이다
# Base를 상속받았기 때문에 ORM 모델이 된다
class Task(Base):

    __tablename__ = "tasks"   
    # 실제 데이터베이스에서 사용할 테이블 이름

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # id 컬럼
    # Mapped[int]       : 이 변수는 int 타입의 DB 컬럼이다
    # Integer           : 숫자로 저장
    # primary_key=True  : 이 테이블에서 가장 중요한 대표 번호
    # index=True        : 빠르게 찾을 수 있도록 색인 생성

    title: Mapped[str] = mapped_column(String(100), index=True)
    # title 컬럼
    # String(100)       : 최대 100글자까지 저장 가능
    # index=True        : 제목으로 검색할 일이 많으니까 빠르게 찾도록 설정

    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    # description 컬럼
    # Optional[str]     : 값이 없어도 되는 글자
    # String(500)       : 최대 500글자까지 저장
    # nullable=True     : 비어 있어도 OK
    
    completed: Mapped[bool] = mapped_column(Boolean, default=False, server_default='false')
    # completed 컬럼
    # Boolean           : 참(True) / 거짓(False) 값
    # default=False     : 파이썬에서 기본값은 False
    # server_default    : DB에서도 기본값을 False로 설정


    # 객체를 print 했을 때 보기 좋게 출력해주는 함수
    # 개발자가 디버깅할 때 편하게 보려고 만드는 것
    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', completed={self.completed})>"