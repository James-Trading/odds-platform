from fastapi import (
    Depends, 
    FastAPI, 
    HTTPException, 
    WebSocket,
    WebSocketDisconnect,
    status,
)

import asyncio

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from client_save_load import load_clients
from distribution.feed_functions import get_client_feed
from save_load import load_platform

from datetime import datetime, timezone

from logs.activity_logger import log_activity

app = FastAPI(
    title="Goldliner Trading Matrix API",
    description="Customer-facing sportsbook odds feed.",
    version="0.2.0",
)

bearer_scheme = HTTPBearer()


def get_authenticated_client(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    api_key = credentials.credentials
    clients = load_clients()

    for client in clients:
        stored_key = client.get("feed", {}).get("api_key")

        if stored_key == api_key:
            if client.get("status", "").lower() != "active":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Client account is inactive.",
                )

            if not client.get("feed", {}).get("enabled", False):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Client feed is disabled.",
                )

            return client

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key.",
        headers={"WWW-Authenticate": "Bearer"},
    )

def get_client_from_api_key(api_key):
    clients = load_clients()

    for client in clients:
        stored_key = client.get("feed", {}).get("api_key")

        if stored_key != api_key:
            continue

        if client.get("status", "").lower() != "active":
            return None

        if not client.get("feed", {}).get("enabled", False):
            return None

@app.get("/")
def api_home():
    return {
        "service": "Goldliner Trading Matrix API",
        "status": "running",
    }


@app.get("/events")
def get_events(client: dict = Depends(get_authenticated_client)):
    platform = load_platform()

    return get_client_feed(
        platform,
        client,
    )

@app.get("/api/v1/feed")
def get_client_feed_v1(
    client: dict = Depends(get_authenticated_client),
):
    platform = load_platform()
    events = get_client_feed(platform, client)

    log_activity(
        "API",
        f"{client.get('name', 'Unknown client')} requested feed "
        f"({len(events)} published events)"
    )

    return {
        "provider": "Goldliner Trading Matrix",
        "api_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "client": {
            "name": client.get("name"),
        },
        "event_count": len(events),
        "events": events,
    }

@app.websocket("/api/v1/live")
async def live_feed(websocket: WebSocket):
    api_key = websocket.query_params.get("api_key")
    client = get_client_from_api_key(api_key)

    if client is None:
        await websocket.close(
            code=1008,
            reason="Invalid API key or disabled client.",
        )
        return

    await websocket.accept()

    client_name = client.get("name", "Unknown client")

    log_activity(
        "WEBSOCKET",
        f"{client_name} connected to live feed",
    )

    last_versions = {}

    try:
        while True:
            platform = load_platform()
            events = get_client_feed(platform, client)

            changed_events = []

            for event in events:
                event_id = event.get("id")
                current_version = event.get("version", 0)
                previous_version = last_versions.get(event_id)

                if (
                    previous_version is None
                    or current_version > previous_version
                ):
                    changed_events.append(event)

                last_versions[event_id] = current_version

            if changed_events:
                await websocket.send_json(
                    {
                        "type": "feed_update",
                        "provider": "Goldliner Trading Matrix",
                        "client": client_name,
                        "event_count": len(changed_events),
                        "events": changed_events,
                    }
                )

                log_activity(
                    "WEBSOCKET",
                    (
                        f"{client_name} received "
                        f"{len(changed_events)} changed events"
                    ),
                )

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        log_activity(
            "WEBSOCKET",
            f"{client_name} disconnected from live feed",
        )