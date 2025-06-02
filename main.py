from fastapi import FastAPI, HTTPException, Depends, Form, Path
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models import User, Base
from database import engine, SessionLocal
from logger import logger


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@app.post("/register")
def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    logger.info(f"Register attempt: username={username}, email={email}")
    user = db.query(User).filter((User.username == username) | (User.email == email)).first()
    if user:
        logger.warning(f"Registration failed: Username or email already registered ({username}, {email})")
        raise HTTPException(status_code=400, detail="Username or email already registered")
    hashed_password = get_password_hash(password)
    new_user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"User registered successfully: username={username}, email={email}")
    return {"msg": "User registered successfully"}

@app.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    logger.info(f"Login attempt: username={username}")
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        logger.warning(f"Failed login attempt for username: {username}")
        raise HTTPException(status_code=400, detail="Invalid credentials")
    logger.info(f"User logged in successfully: username={username}")
    return {"msg": "Login successful"}

@app.post("/reset-password")
def reset_password(
    email: str = Form(...),
    old_password: str = Form(...),
    new_password: str = Form(...),
    db: Session = Depends(get_db)
):
    logger.info(f"Password reset attempt for email: {email}")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        logger.warning(f"Password reset failed: User not found for email {email}")
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(old_password, user.hashed_password):
        logger.warning(f"Password reset failed: Incorrect old password for email {email}")
        raise HTTPException(status_code=400, detail="Incorrect old password")
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    logger.info(f"Password reset successful for email: {email}")
    return {"msg": "Password reset successful"}

@app.get("/user/{user_id}")
def get_user(user_id: int = Path(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"User not found for id: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"User info retrieved for id {user_id}: username={user.username}, email={user.email}")
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email
    }
