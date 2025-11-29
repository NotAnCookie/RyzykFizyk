from fastapi import FastAPI
from routers import verify

app = FastAPI(title="Quiz Backend")

# app.include_router(questions.router)
# app.include_router(trivia.router)
app.include_router(verify.router)
