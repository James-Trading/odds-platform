import uuid
from datetime import datetime, timezone

from state.change_sequence import (
    next_change_id,
    log_event_change,
)

def create_event(category, event_class, event_type, event_name):
    return {
        "id": str(uuid.uuid4()),
        "category": category,
        "class": event_class,
        "type": event_type,
        "event_name": event_name,
        "status": "draft",
        "displayed": True,
        "published": False,
        "archived": False,
        "start_time": "",
        "suspend_mode": "AUTO",
        "version": 1,
        "change_id": next_change_id(),
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "markets": []
    }


def create_market(event, market_name):
    market = {
        "id": str(uuid.uuid4()),
        "name": market_name,
        "status": "Trading",
        "published": False,
        "displayed": True,

        "limits": {
            "max_win_per_customer": 500,
            "max_liability": 5000
        },

        "notes": "",

        "selections": []
    }

    event["markets"].append(market)

    return market


def add_selection(market, selection_name, price):
    selection = {
        "id": str(uuid.uuid4()),
        "name": selection_name,
        "price": price,
        "pending_price": None,
        "price_history": [
            {
                "created": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "price": price,
            }
        ],
        "active": True,
        "displayed": True,
        "result": "",
    }

    market["selections"].append(selection)

    return selection

def touch_event(event, change_type="event_update", details=None):
    event["version"] = event.get("version", 0) + 1
    event["change_id"] = next_change_id()
    event["last_updated"] = datetime.now(
        timezone.utc
    ).isoformat()

    log_event_change(
        event,
        change_type=change_type,
        details=details,
    )