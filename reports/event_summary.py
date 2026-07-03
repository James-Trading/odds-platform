def display_event_summary(event):

    print()
    print("=" * 50)
    print(event["event_name"].upper())
    print("=" * 50)
    print()

    print(f"Category : {event['category']}")
    print(f"Class    : {event['class']}")
    print(f"Type     : {event['type']}")
    print()

    market_count = len(event["markets"])

    selection_count = 0
    active_markets = 0
    suspended_markets = 0
    active_selections = 0
    suspended_selections = 0

    for market in event["markets"]:

        if market["status"] == "Trading":
            active_markets += 1
        else:
            suspended_markets += 1

        for selection in market["selections"]:

            selection_count += 1

            if selection["active"]:
                active_selections += 1
            else:
                suspended_selections += 1

    print(f"Markets              : {market_count}")
    print(f"Selections           : {selection_count}")
    print()
    print(f"Active Markets       : {active_markets}")
    print(f"Suspended Markets    : {suspended_markets}")
    print()
    print(f"Active Selections    : {active_selections}")
    print(f"Suspended Selections : {suspended_selections}")
    print()
    print("MARKETS")
    print("=======")

    for market in event["markets"]:
        status = "🟢"

        if market["status"] != "Trading":
            status = "🔴"

        print(f"{status} {market['name']}")