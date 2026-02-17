from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from .database import init_db
from .routers import rooms, movies, votes


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="CineMatch API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://demo.cinematch.umans.ai"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rooms.router, prefix="/api/v1/rooms", tags=["rooms"])
app.include_router(movies.router, prefix="/api/v1/movies", tags=["movies"])
app.include_router(votes.router, prefix="/api/v1/votes", tags=["votes"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
