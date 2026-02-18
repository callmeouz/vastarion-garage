from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app import models
from app.database import engine
from routers import auth, vehicles, users

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vastarion Garage API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(vehicles.router)
app.include_router(users.router)

@app.get("/")
def read_root():
    return {"message": "Vastarion System Online!"}
