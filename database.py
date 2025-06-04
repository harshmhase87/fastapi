from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:4545@localhost/fastapi_auth"

engine = create_engine(SQLALCHEMY_DATABASE_URL)  # इथे SQLALCHEMY_DATABASE_URL वापरा
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
