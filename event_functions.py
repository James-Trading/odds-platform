def create_event(category, event_class, event_type, event_name):
    return {
        "category": category,
        "class": event_class,
        "type": event_type,
        "event_name": event_name,
        "status": "Active",
        "displayed": True,
        "published": False,
        "start_time": "",
        "suspend_mode": "AUTO",
        "markets": []
    }


def create_market(event, market_name):
    market = {
        "name": market_name,
        "status": "Active",
        "published": False,
        "displayed": True,
        "selections": []
    }

    event["markets"].append(market)

    return market


def add_selection(market, selection_name, price):
    market["selections"].append(
        {
            "name": selection_name,
            "price": price,
            "pending_price": None,
            "active": True,
            "displayed": True,
            "result": ""
        }
    )