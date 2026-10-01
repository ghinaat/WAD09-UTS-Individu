from copy import deepcopy
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware

from .data import SESSIONS
from .models import SessionCreate, SessionOut

app = FastAPI(title="Campus Shuttle Sessions", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions_db: list[SessionOut] = [SessionOut.model_validate(session) for session in SESSIONS]
_next_id = max((session.id for session in sessions_db), default=0) + 1


@app.get("/")
def home() -> dict[str, str]:
    return {"message": "Campus Shuttle Sessions API is running"}


@app.get("/sessions")
def list_sessions(
    page: int = Query(1, ge=1),
    limit: int = Query(5, ge=1, le=20),
    search: str = Query(default=""),
) -> dict[str, Any]:
    keyword = search.strip().lower()

    items = [session.model_dump() for session in sessions_db]
    if keyword:
        items = [
            item
            for item in items
            if keyword in " ".join(
                [
                    str(item.get("route_name", "")),
                    str(item.get("driver_name", "")),
                    str(item.get("passenger_name", "")),
                    str(item.get("destination", "")),
                ]
            ).lower()
        ]

    total = len(items)
    start = (page - 1) * limit
    paginated = items[start : start + limit]

    return {
        "items": paginated,
        "page": page,
        "limit": limit,
        "total": total,
        "pages": (total + limit - 1) // limit if total else 0,
    }


@app.get("/sessions/{session_id}", response_model=SessionOut)
def get_session(session_id: int) -> SessionOut:
    session = next((item for item in sessions_db if item.id == session_id), None)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@app.post("/sessions", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def create_session(payload: SessionCreate) -> SessionOut:
    global _next_id
    new_session = SessionOut(id=_next_id, **payload.model_dump())
    sessions_db.append(new_session)
    _next_id += 1
    return new_session


@app.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: int) -> Response:
    for index, session in enumerate(sessions_db):
        if session.id == session_id:
            del sessions_db[index]
            return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail="Session not found")
