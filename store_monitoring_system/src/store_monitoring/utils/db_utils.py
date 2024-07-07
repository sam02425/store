from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..models.database import Base

DATABASE_URL = "postgresql://user:password@localhost/store_monitoring"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()