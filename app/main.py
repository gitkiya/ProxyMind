from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from psycopg2.extras import RealDictCursor

from sqlalchemy.orm import Session
from . import model
from .database import engine
from .router import post , user, auth , vote

model.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
       
app.include_router(post.router)        
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

    
@app.get("/")
def root():
    return {"message": "Hello!! World"}






