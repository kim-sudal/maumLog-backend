from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 환경 변수에 DATABASE_URL이 없으면 기본값 사용
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:mysql@localhost:3306/service1")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
