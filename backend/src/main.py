from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.src.modules.auth import router

app = FastAPI(title="DefectMind API")

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(router)


@app.get("/")
async def root():
    return {"message": "DefectMind API is running"}
