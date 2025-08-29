from datetime import timedelta
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI ,HTTPException, status, staticfiles,  Request, Depends
from fastapi.security import OAuth2PasswordRequestForm
from auth import auth_main, token
from dependencies import injections
from store.pydantics import user_models
from store import models
from routes import users, products, sale, statistics
from dependencies import injections
import time
import logging
logging.basicConfig(level=logging.INFO)



my_app = FastAPI()
my_app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://medical-berna-privet-65c89d59.koyeb.app", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

my_app.include_router(users.router)
my_app.include_router(products.router)
my_app.include_router(sale.router)
my_app.include_router(statistics.router)
my_app.add_middleware(SessionMiddleware, secret_key="gugiuggbgjkh")
my_app.mount("/static", staticfiles.StaticFiles(directory="static/"), name="static")


@my_app.middleware("https")
async def log_request_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logging.info(f"{request.method} {request.url} - {response.status_code} - Took {process_time:.4f} seconds")
    return response

@my_app.get("/", response_model=user_models.UserOut)
async def welcome(user = injections.user_or_admin, db = injections.database_dep):
    user_data = db.query(models.User).filter(models.User.id == user.id).first()
    return user_data


@my_app.post("/token")
async def login(user_token : OAuth2PasswordRequestForm = Depends(),database = injections.database_dep):
    user = auth_main.authenticate_user(user_token.username,user_token.password, database)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Could not validated the User")
    created_token = token.create_access_token(user.username, user.id, timedelta(minutes=1000))
    return {"access_token": created_token, "token_type": "bearer","user":user}



