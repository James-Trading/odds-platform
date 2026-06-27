def calculate_selection_liability(
    bets,
    event_name,
    market_name,
    selection_name,
):

    total_stakes = 0
    payout = 0

    for bet in bets:

        if bet["status"] != "Open":
            continue

        if bet["event"] != event_name:
            continue

        if bet["market"] != market_name:
            continue

        total_stakes += bet["stake"]

        if bet["selection"] == selection_name:

            top = bet["price"][0]
            bottom = bet["price"][1]

            payout += bet["stake"] * (top / bottom)
            payout += bet["stake"]

    return total_stakes - payout

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

    print("Selection | Win P/L")
    print("-------------------")

    for selection in market["selections"]:

        liability = calculate_selection_liability(
            bets,
            event["event_name"],
            market["name"],
            selection["name"]
        )

        print(
            selection["name"],
            "|",
            f"£{liability:.2f}"
        )