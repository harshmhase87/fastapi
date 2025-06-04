from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# MySQL database URL
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:4545@localhost/fastapi_auth"

# SQLAlchemy engine setup
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Session creation
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
