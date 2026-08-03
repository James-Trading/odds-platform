from fastapi import Depends, FastAPI, HTTPException, status
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
