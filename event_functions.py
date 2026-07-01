import uuid
from datetime import datetime
def create_event(category, event_class, event_type, event_name):
    return {
        "id": str(uuid.uuid4()),
        "category": category,
        "class": event_class,
        "type": event_type,
        "event_name": event_name,
        "status": "Trading",
        "displayed": True,
        "published": False,
        "start_time": "",
        "suspend_mode": "AUTO",
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
    market["selections"].append(
        {
            "id": str(uuid.uuid4()),
            "name": selection_name,
            "price": price,
            "pending_price": None,
            "price_history": [
                {
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "price": price
                }
            ],
            "active": True,
            "displayed": True,
            "result": ""
        }
    )