from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.src.core.neo4j_db import close_neo4j_driver, init_neo4j_driver
from backend.src.modules.auth.router import router as auth_router
from backend.src.modules.users.router import router as users_router
from backend.src.modules.artifacts.router import router as artifacts_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_neo4j_driver()
    yield
    # Shutdown
    close_neo4j_driver()


app = FastAPI(title="DefectMind API", lifespan=lifespan)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router, tags=["auth"])
app.include_router(users_router, prefix="/api/v1", tags=["users"])
app.include_router(artifacts_router, prefix="/api/v1", tags=["artifacts"])
