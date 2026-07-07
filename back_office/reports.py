def display_market_report(platform):

    print()
    print("=" * 50)
    print("MARKET REPORT")
    print("=" * 50)
    print()

    for event in platform:

        print(event["event_name"])
        print("-" * 50)

        for market in event.get("markets", []):

            status = "ACTIVE"

            if not market.get("active", True):
                status = "SUSPENDED"

            published = "YES" if market.get("published", False) else "NO"

            print(
                f"{market['name']} | "
                f"Selections: {len(market.get('selections', []))} | "
                f"Status: {status} | "
                f"Published: {published}"
            )

        print()

def display_event_report(platform):

    print()
    print("=" * 50)
    print("EVENT REPORT")
    print("=" * 50)
    print()

    for event in platform:

        markets = len(event.get("markets", []))

        active = "YES" if event.get("active", True) else "NO"

        print(
            f"{event['event_name']}\n"
            f"Category : {event['category']}\n"
            f"Markets  : {markets}\n"
            f"Active   : {active}\n"
        )