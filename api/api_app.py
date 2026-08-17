from fastapi import (
    Depends, 
    FastAPI, 
    HTTPException, 
    WebSocket,
    WebSocketDisconnect,
    status,
)

from pydantic import BaseModel, Field

import asyncio

import os

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from client_save_load import load_clients
from distribution.feed_functions import get_client_feed
from save_load import load_platform, save_platform

from price_engine.price_ladder import set_price
from event_functions import touch_event

from datetime import datetime, timezone

from logs.activity_logger import log_activity

from state.change_sequence import load_change_log

app = FastAPI(
    title="Goldliner Trading Matrix API",
    description="Customer-facing sportsbook odds feed.",
    version="0.2.0",
)

bearer_scheme = HTTPBearer()

active_websocket_clients = {}

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

        return client
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

@app.get("/api/v1/changes")
def get_client_changes(
    since: int = 0,
    client: dict = Depends(get_authenticated_client),
):
    platform = load_platform()

    client_events = get_client_feed(
        platform,
        client,
    )

    allowed_event_ids = {
        event.get("id")
        for event in client_events
        if event.get("id")
    }

    all_changes = load_change_log()

    client_changes = [
        change
        for change in all_changes
        if (
            change.get("change_id", 0) > since
            and change.get("event_id") in allowed_event_ids
        )
    ]

    latest_change_id = max(
        (
            change.get("change_id", 0)
            for change in all_changes
        ),
        default=since,
    )

    log_activity(
        "API",
        f"{client.get('name', 'Unknown client')} requested "
        f"changes since {since} - "
        f"{len(client_changes)} changes returned",
    )

    return {
        "provider": "Goldliner Trading Matrix",
        "api_version": "1.0",
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "since": since,
        "latest_change_id": latest_change_id,
        "change_count": len(client_changes),
        "changes": client_changes,
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

    active_websocket_clients[client_name] = {
        "connected": True,
        "connected_at": datetime.now(timezone.utc).isoformat(),
        "last_update_sent": None,
    }

    log_activity(
        "WEBSOCKET",
        f"{client_name} connected to live feed",
    )

    last_versions = {}

    try:
        while True:
            current_client = get_client_from_api_key(api_key)

            if current_client is None:
                await websocket.close(
                    code=1008,
                    reason="Client access revoked.",
                )
                return

            client = current_client

            platform = load_platform()
            events = get_client_feed(platform, client)

            current_versions = {
                event.get("id"): event.get("version", 0)
                for event in events
                if event.get("id")
            }

            if current_versions != last_versions:
                await websocket.send_json(
                    {
                        "type": "feed_update",
                        "provider": "Goldliner Trading Matrix",
                        "client": client_name,
                        "event_count": len(events),
                        "events": events,
                    }
                )

                active_websocket_clients[client_name][
                    "last_update_sent"
                ] = datetime.now(timezone.utc).isoformat()

                log_activity(
                    "WEBSOCKET",
                    (
                        f"{client_name} received feed update "
                        f"({len(events)} events)"
                    ),
                )

                last_versions = current_versions

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        if client_name in active_websocket_clients:
            active_websocket_clients[client_name][
                "connected"
            ] = False

        log_activity(
            "WEBSOCKET",
            f"{client_name} disconnected from live feed",
        )

@app.get("/internal/connections")
def get_active_connections():
    return {
        "connection_count": sum(
            1
            for client in active_websocket_clients.values()
            if client.get("connected")
        ),
        "clients": active_websocket_clients,
    }

ADMIN_API_KEY = os.getenv("GTM_ADMIN_API_KEY")


def get_authenticated_admin(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    if not ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin API key is not configured.",
        )

    if credentials.credentials != ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin API key.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return True

class AdminPriceChangeRequest(BaseModel):
    event_id: str
    market_id: str
    selection_id: str
    price_top: int = Field(gt=0)
    price_bottom: int = Field(gt=0)


@app.get("/internal/admin/platform")
def get_admin_platform(
    _: bool = Depends(get_authenticated_admin),
):
    return load_platform()

@app.post("/internal/admin/price")
def admin_change_price(
    request: AdminPriceChangeRequest,
    _: bool = Depends(get_authenticated_admin),
):
    platform = load_platform()

    event = next(
        (
            event
            for event in platform
            if event.get("id") == request.event_id
        ),
        None,
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found.",
        )

    market = next(
        (
            market
            for market in event.get("markets", [])
            if market.get("id") == request.market_id
        ),
        None,
    )

    if market is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Market not found.",
        )

    selection = next(
        (
            selection
            for selection in market.get("selections", [])
            if selection.get("id") == request.selection_id
        ),
        None,
    )

    if selection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Selection not found.",
        )

    old_price = selection.get("price")

    set_price(
        selection,
        request.price_top,
        request.price_bottom,
    )

    touch_event(
        event,
        change_type="price_change",
        details={
            "market_id": market.get("id"),
            "market_name": market.get("name"),
            "selection_id": selection.get("id"),
            "selection_name": selection.get("name"),
            "old_price": old_price,
            "new_price": selection.get("price"),
        },
    )

    save_platform(platform)

    return {
        "status": "updated",
        "event_id": event.get("id"),
        "market_id": market.get("id"),
        "selection_id": selection.get("id"),
        "selection_name": selection.get("name"),
        "old_price": old_price,
        "new_price": selection.get("price"),
        "version": event.get("version"),
        "change_id": event.get("change_id"),
    }

class AdminSelectionStateRequest(BaseModel):
    event_id: str
    market_id: str
    selection_id: str
    active: bool | None = None
    displayed: bool | None = None

@app.post("/internal/admin/selection-state")
def admin_selection_state(
    request: AdminSelectionStateRequest,
    _: bool = Depends(get_authenticated_admin),
):
    platform = load_platform()

    event = next(
        (e for e in platform if e.get("id") == request.event_id),
        None,
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found.",
        )

    market = next(
        (
            m
            for m in event.get("markets", [])
            if m.get("id") == request.market_id
        ),
        None,
    )

    if market is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Market not found.",
        )

    selection = next(
        (
            s
            for s in market.get("selections", [])
            if s.get("id") == request.selection_id
        ),
        None,
    )

    if selection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Selection not found.",
        )

    old_active = selection.get("active", True)
    old_displayed = selection.get("displayed", True)

    if request.active is not None:
        selection["active"] = request.active

    if request.displayed is not None:
        selection["displayed"] = request.displayed

    touch_event(
        event,
        change_type="selection_state_change",
        details={
            "market_id": market.get("id"),
            "market_name": market.get("name"),
            "selection_id": selection.get("id"),
            "selection_name": selection.get("name"),
            "old_active": old_active,
            "new_active": selection.get("active", True),
            "old_displayed": old_displayed,
            "new_displayed": selection.get("displayed", True),
        },
    )

    save_platform(platform)

    return {
        "status": "updated",
        "selection_id": selection.get("id"),
        "selection_name": selection.get("name"),
        "active": selection.get("active", True),
        "displayed": selection.get("displayed", True),
        "version": event.get("version"),
        "change_id": event.get("change_id"),
    }

class AdminEventStateRequest(BaseModel):
    event_id: str
    active: bool


@app.post("/internal/admin/event-state")
def admin_event_state(
    request: AdminEventStateRequest,
    _: bool = Depends(get_authenticated_admin),
):
    platform = load_platform()

    event = next(
        (
            event
            for event in platform
            if event.get("id") == request.event_id
        ),
        None,
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found.",
        )

    old_active = event.get("active", True)

    event["active"] = request.active

    touch_event(
        event,
        change_type="event_state_change",
        details={
            "old_active": old_active,
            "new_active": event.get("active", True),
        },
    )

    save_platform(platform)

    return {
        "status": "updated",
        "event_id": event.get("id"),
        "event_name": event.get("event_name"),
        "active": event.get("active", True),
        "version": event.get("version"),
        "change_id": event.get("change_id"),
    }

class AdminEventDetailsRequest(BaseModel):
    event_id: str
    event_name: str
    start_time: str
    status: str
    suspend_mode: str


@app.post("/internal/admin/event-details")
def admin_event_details(
    request: AdminEventDetailsRequest,
    _: bool = Depends(get_authenticated_admin),
):
    platform = load_platform()

    event = next(
        (
            event
            for event in platform
            if event.get("id") == request.event_id
        ),
        None,
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found.",
        )

    old_details = {
        "event_name": event.get("event_name"),
        "start_time": event.get("start_time"),
        "status": event.get("status"),
        "suspend_mode": event.get("suspend_mode"),
    }

    event["event_name"] = request.event_name
    event["start_time"] = request.start_time
    event["status"] = request.status
    event["suspend_mode"] = request.suspend_mode

    touch_event(
        event,
        change_type="event_details_change",
        details={
            "old": old_details,
            "new": {
                "event_name": event.get("event_name"),
                "start_time": event.get("start_time"),
                "status": event.get("status"),
                "suspend_mode": event.get("suspend_mode"),
            },
        },
    )

    save_platform(platform)

    return {
        "status": "updated",
        "event_id": event.get("id"),
        "event_name": event.get("event_name"),
        "start_time": event.get("start_time"),
        "event_status": event.get("status"),
        "suspend_mode": event.get("suspend_mode"),
        "version": event.get("version"),
        "change_id": event.get("change_id"),
    }

class AdminMarketStateRequest(BaseModel):
    event_id: str
    market_id: str
    status: str


@app.post("/internal/admin/market-state")
def admin_market_state(
    request: AdminMarketStateRequest,
    _: bool = Depends(get_authenticated_admin),
):
    platform = load_platform()

    event = next(
        (
            event
            for event in platform
            if event.get("id") == request.event_id
        ),
        None,
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found.",
        )

    market = next(
        (
            market
            for market in event.get("markets", [])
            if market.get("id") == request.market_id
        ),
        None,
    )

    if market is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Market not found.",
        )

    old_status = market.get("status", "ACTIVE")
    market["status"] = request.status

    touch_event(
        event,
        change_type="market_state_change",
        details={
            "market_id": market.get("id"),
            "market_name": market.get("name"),
            "old_status": old_status,
            "new_status": market.get("status"),
        },
    )

    save_platform(platform)

    return {
        "status": "updated",
        "event_id": event.get("id"),
        "market_id": market.get("id"),
        "market_name": market.get("name"),
        "market_status": market.get("status"),
        "version": event.get("version"),
        "change_id": event.get("change_id"),
    }

class AdminEventPublishRequest(BaseModel):
    event_id: str
    published: bool


@app.post("/internal/admin/event-publish")
def admin_event_publish(
    request: AdminEventPublishRequest,
    _: bool = Depends(get_authenticated_admin),
):
    platform = load_platform()

    event = next(
        (
            event
            for event in platform
            if event.get("id") == request.event_id
        ),
        None,
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found.",
        )

    old_published = event.get("published", False)
    event["published"] = request.published

    touch_event(
        event,
        change_type="event_publish_change",
        details={
            "old_published": old_published,
            "new_published": event.get("published", False),
        },
    )

    save_platform(platform)

    return {
        "status": "updated",
        "event_id": event.get("id"),
        "published": event.get("published", False),
        "version": event.get("version"),
        "change_id": event.get("change_id"),
    }