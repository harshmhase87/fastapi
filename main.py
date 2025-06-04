from fastapi import FastAPI, HTTPException, Depends, Form, Path, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from models import User, Base
from database import engine, SessionLocal
from logger import logger

app = FastAPI()

# Static files आणि Templates mount
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# DB initialization
Base.metadata.create_all(bind=engine)

# Dependency - Get DB Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utility - Password Hashing
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# 🏠 Home redirects to login
@app.get("/", response_class=HTMLResponse)
def home():
    return RedirectResponse("/login")


# 🔐 REGISTER
@app.get("/register", response_class=HTMLResponse)
def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register", response_class=HTMLResponse)
def register_post(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    logger.info(f"Register attempt: {username}, {email}")
    user = db.query(User).filter((User.username == username) | (User.email == email)).first()
    if user:
        msg = "Username or email already registered"
        logger.warning(msg)
        return templates.TemplateResponse("register.html", {"request": request, "error": msg})
    
    hashed_password = get_password_hash(password)
    new_user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    msg = f"User {username} registered successfully!"
    logger.info(msg)
    return templates.TemplateResponse("register.html", {"request": request, "message": msg})


# 🔑 LOGIN
@app.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    logger.info(f"Login attempt: {username}")
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        msg = "Invalid credentials"
        logger.warning(msg)
        return templates.TemplateResponse("login.html", {"request": request, "error": msg})

    msg = f"Welcome back, {username}!"
    logger.info(msg)
    return templates.TemplateResponse("login.html", {"request": request, "message": msg})


# 🔁 RESET PASSWORD
@app.get("/reset-password", response_class=HTMLResponse)
def reset_password_get(request: Request):
    return templates.TemplateResponse("reset_password.html", {"request": request})


@app.post("/reset-password", response_class=HTMLResponse)
def reset_password_post(
    request: Request,
    email: str = Form(...),
    old_password: str = Form(...),
    new_password: str = Form(...),
    db: Session = Depends(get_db)
):
    logger.info(f"Password reset attempt: {email}")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        msg = "User not found"
        logger.warning(msg)
        return templates.TemplateResponse("reset_password.html", {"request": request, "error": msg})

    if not verify_password(old_password, user.hashed_password):
        msg = "Incorrect old password"
        logger.warning(msg)
        return templates.TemplateResponse("reset_password.html", {"request": request, "error": msg})

    user.hashed_password = get_password_hash(new_password)
    db.commit()

    msg = "Password reset successful!"
    logger.info(msg)
    return templates.TemplateResponse("reset_password.html", {"request": request, "message": msg})


# 👤 Get User Info (Optional)
@app.get("/user/{user_id}")
def get_user(user_id: int = Path(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "username": user.username, "email": user.email}
