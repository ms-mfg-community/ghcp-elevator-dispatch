from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager, suppress
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator

from api.database import create_database_engine, dispose_database_engine, ensure_database_schema
from simulation.floors import is_supported_floor, supported_floor_error
from simulation.simulation import SimulationEngine

BASE_DIR = Path(__file__).resolve().parent.parent
engine = SimulationEngine(tick_interval=1.0)


class PassengerRequest(BaseModel):
    origin_floor: int
    destination_floor: int

    @field_validator("origin_floor", "destination_floor")
    @classmethod
    def supported_floor(cls, value: int) -> int:
        if not is_supported_floor(value):
            raise ValueError(supported_floor_error())
        return value


class ControlRequest(BaseModel):
    paused: bool


@asynccontextmanager
async def lifespan(application: FastAPI):
    database_engine = create_database_engine()
    application.state.database_engine = database_engine
    await ensure_database_schema(database_engine)
    engine.set_database_engine(database_engine)
    task = asyncio.create_task(engine.run())
    try:
        yield
    finally:
        await engine.shutdown()
        await dispose_database_engine(database_engine)
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task


app = FastAPI(title="Elevator Dispatch Workshop", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=BASE_DIR /
          "ui" / "static"), name="static")


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(BASE_DIR / "ui" / "templates" / "index.html")


@app.get("/api/state")
async def get_state() -> dict[str, object]:
    return await engine.get_state()


@app.post("/api/passengers", status_code=201)
async def create_passenger(payload: PassengerRequest) -> dict[str, object]:
    if payload.origin_floor == payload.destination_floor:
        raise HTTPException(
            status_code=400, detail="Origin and destination floors must differ.")
    return await engine.add_passenger(payload.origin_floor, payload.destination_floor)


@app.post("/api/control")
async def control_simulation(payload: ControlRequest) -> dict[str, object]:
    return await engine.set_paused(payload.paused)


@app.post("/api/restart")
async def restart_simulation() -> dict[str, object]:
    return await engine.restart()


@app.websocket("/ws")
async def websocket_state(websocket: WebSocket) -> None:
    await websocket.accept()
    queue = await engine.subscribe()
    try:
        await websocket.send_json(await engine.get_state())
        while True:
            snapshot = await queue.get()
            await websocket.send_json(snapshot)
    except WebSocketDisconnect:
        pass
    finally:
        await engine.unsubscribe(queue)
