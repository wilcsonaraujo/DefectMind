from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.src.modules.auth import router
from backend.src.modules.users.router import router as users_router

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
app.include_router(users_router, prefix="/api/v1", tags=["users"])
