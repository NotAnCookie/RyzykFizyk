from fastapi import FastAPI
from app.routers import verify
from app.routers import questions

app = FastAPI(title="Quiz Backend")

app.include_router(questions.router)
# app.include_router(trivia.router)
app.include_router(verify.router)
