def calculate_market_turnover(bets, event, market):

    turnover = 0

    for bet in bets:

        if bet.get("event_id", bet["event"]) != event.get("id", event["event_name"]):
            continue

        if bet.get("market_id", bet["market"]) != market.get("id", market["name"]):
            continue

        turnover += bet["stake"]

    return turnover


def count_market_bets(bets, event, market):

    count = 0

    for bet in bets:

        if bet.get("event_id", bet["event"]) != event.get("id", event["event_name"]):
            continue

        if bet.get("market_id", bet["market"]) != market.get("id", market["name"]):
            continue

        count += 1

    return count

def count_open_market_bets(bets, event, market):

    count = 0

    for bet in bets:

        if bet.get("event_id", bet["event"]) != event.get("id", event["event_name"]):
            continue

        if bet.get("market_id", bet["market"]) != market.get("id", market["name"]):
            continue

        if bet["status"] == "Open":
            count += 1

    return count


def count_settled_market_bets(bets, event, market):

    count = 0

    for bet in bets:

        if bet.get("event_id", bet["event"]) != event.get("id", event["event_name"]):
            continue

        if bet.get("market_id", bet["market"]) != market.get("id", market["name"]):
            continue

        if bet["settled"]:
            count += 1

    return count

def display_market_report(bets, event, market):

    turnover = calculate_market_turnover(
        bets,
        event,
        market
    )

    bet_count = count_market_bets(
        bets,
        event,
        market
    )

    open_bets = count_open_market_bets(bets, event, market)

    settled_bets = count_settled_market_bets(bets, event, market)

    returns = calculate_market_returns(bets, event, market)

    gw = turnover - returns

    gw_percentage = calculate_market_gw_percentage(
        turnover,
        gw
    )

    print()
    print("MARKET REPORT")
    print("=============")
    print()
    print(event["event_name"])
    print(market["name"])
    print()
    print(f"Turnover : £{round(turnover)}")
    print(f"Bets     : {bet_count}")
    print(f"Open Bets    {open_bets}")
    print(f"Settled Bets {settled_bets}")
    print(f"Returns      £{round(returns)}")
    print(f"GW           £{round(gw)}")
    print(f"GW           £{round(gw)}")
    print(f"GW%          {gw_percentage:.1f}%")

    input("\nPress Enter to continue...")

def calculate_market_returns(bets, event, market):

    total_returns = 0

    for bet in bets:

        if bet.get("event_id", bet["event"]) != event.get("id", event["event_name"]):
            continue

        if bet.get("market_id", bet["market"]) != market.get("id", market["name"]):
            continue

        if bet["result"] != "Won":
            continue

        top = bet["price"][0]
        bottom = bet["price"][1]

        total_returns += bet["stake"] * (top / bottom)
        total_returns += bet["stake"]

    return total_returns

def calculate_market_gw_percentage(turnover, gw):

    if turnover == 0:
        return 0

    return (gw / turnover) * 100