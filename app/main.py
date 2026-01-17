# app/main.py

from fastapi import FastAPI
from .routers import tasks, auth
from .routers import users  
from fastapi.responses import ORJSONResponse
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI(
    title="ToDo List API - 실전 프로젝트",
    default_response_class=ORJSONResponse
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


app.include_router(
    tasks.router,       
    prefix="/tasks",   
    tags=["Tasks"]      
)


app.include_router(
    users.router,      
    prefix="/users",    
    tags=["Users"]      
)

app.include_router(
    auth.router, 
    tags=["Authentication"]    
)


@app.get("/")
async def root():
    return {"message": "Welcome to the ToDo List API!"}