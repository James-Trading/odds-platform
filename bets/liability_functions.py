def calculate_selection_liability(
    bets,
    event_id,
    market_id,
    selection_id,
):

    total_stakes = 0
    payout = 0

    for bet in bets:

        if bet["status"] != "Open":
            continue

        if bet.get("event_id", bet["event"]) != event_id:
            continue

        if bet.get("market_id", bet["market"]) != market_id:
            continue

        total_stakes += bet["stake"]

        if bet.get("selection_id", bet["selection"]) == selection_id:

            top = bet["price"][0]
            bottom = bet["price"][1]

            payout += bet["stake"] * (top / bottom)
            payout += bet["stake"]

    return total_stakes - payout

def calculate_selection_stakes(
    bets,
    event_id,
    market_id,
    selection_id,
):

    total = 0

    for bet in bets:

        if bet["status"] != "Open":
            continue

        if bet.get("event_id", bet["event"]) != event_id:
            continue

        if bet.get("market_id", bet["market"]) != market_id:
            continue

        if bet.get("selection_id", bet["selection"]) == selection_id:
            total += bet["stake"]

    return total

def display_market_liability(
    bets,
    event,
    market
):

    print()
    print("MARKET LIABILITY")
    print("================")
    print(event["event_name"])
    print(market["name"])
    print()

    print("Selection | Price | Stakes | Win P/L")
    print("------------------------------------")

    worst_selection = None
    worst_liability = None

    for selection in market["selections"]:

        price = selection["price"]

        price_display = (
            str(price[0])
            + "/"
            + str(price[1])
        )

        stakes = calculate_selection_stakes(
            bets,
            event.get("id", event["event_name"]),
            market.get("id", market["name"]),
            selection.get("id", selection["name"])
        )

        liability = calculate_selection_liability(
            bets,
            event.get("id", event["event_name"]),
            market.get("id", market["name"]),
            selection.get("id", selection["name"])
        )

        if worst_liability is None or liability < worst_liability:

            worst_liability = liability
            worst_selection = selection["name"]

        print(
            selection["name"],
            "|",
            price_display,
            "|",
            f"£{stakes:.2f}",
            "|",
            f"£{liability:.2f}"
        )

    print()
    print(f"Worst Position: {worst_selection} £{worst_liability:.2f}")

def get_selection_liability(
    bets,
    event,
    market,
    selection
):

    return calculate_selection_liability(
        bets,
        event.get("id", event["event_name"]),
        market.get("id", market["name"]),
        selection.get("id", selection["name"])
    )