def change_price(market, selection_name, new_price):
    for selection in market:
        if selection["name"] == selection_name:
            selection["price"] = new_price


def suspend_runner(market, selection_name):
    for selection in market:
        if selection["name"] == selection_name:
            selection["active"] = False


def settle_market(market, winner_name):
    for selection in market:
        if selection["name"] == winner_name:
            selection["result"] = "Winner"
        else:
            selection["result"] = "Loser"


def add_runner(market, selection_name, price):
    market.append(
        {
            "name": selection_name,
            "price": price,
            "active": True,
            "result": ""
        }
    )

def find_market(event, market_name):
    for market in event["markets"]:
        if market["name"] == market_name:
            return market


def change_event_price(event, market_name, selection_name, new_price):
    market = find_market(event, market_name)

    for selection in market["selections"]:
        if selection["name"] == selection_name:
            selection["price"] = new_price

def suspend_market(event, market_name):
    market = find_market(event, market_name)

    if market:
        market["status"] = "SUSPENDED"     

def open_market(event, market_name):
    market = find_market(event, market_name)

    if market:
        market["status"] = "ACTIVE"

def hide_selection(event, market_name, selection_name):
    market = find_market(event, market_name)

    if market:
        for selection in market["selections"]:
            if selection["name"] == selection_name:
                selection["displayed"] = False


def show_selection(event, market_name, selection_name):
    market = find_market(event, market_name)

    if market:
        for selection in market["selections"]:
            if selection["name"] == selection_name:
                selection["displayed"] = True


def hide_market(event, market_name):
    market = find_market(event, market_name)

    if market:
        market["displayed"] = False


def show_market(event, market_name):
    market = find_market(event, market_name)

    if market:
        market["displayed"] = True 

def suspend_market(market):

    market["status"] = "SUSPENDED"

    for selection in market["selections"]:

        selection["active"] = False                      