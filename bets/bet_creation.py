import uuid
from datetime import datetime


def create_bet(
    client,
    event,
    market,
    selection,
    stake,
    price,
    event_id,
    market_id,
    selection_id,
):

    return {

        "id": str(uuid.uuid4()),

        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        "client": client,

        "event_id": event_id,
        "market_id": market_id,
        "selection_id": selection_id,

        "event": event,

        "market": market,

        "selection": selection,

        "stake": stake,

        "price": price,

        "status": "Open",

        "settled": False,

        "result": None
    }