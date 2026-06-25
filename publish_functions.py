def publish_event(
        clients,
        event):

    print()
    print(f"Publishing {event['event_name']}")
    print("=" * (11 + len(event["event_name"])))
    print()

    market_count = len(event["markets"])

    selection_count = 0

    for market in event["markets"]:

        selection_count = selection_count + len(market["selections"])

    published = 0

    for client in clients:

        if event["event_name"] in client["booked_events"]:

            print(f"✓ {client['name']}")
            print(f"  Markets: {market_count}")
            print(f"  Selections: {selection_count}")
            print()

            for market in event["markets"]:

                print(" ", market["name"])
                print(" ", "-" * len(market["name"]))

                for selection in market["selections"]:

                    if selection["displayed"]:

                        top = selection["price"][0]
                        bottom = selection["price"][1]

                        print(
                            " ",
                            selection["name"],
                            str(top) + "/" + str(bottom)
                        )

            print()

            published = published + 1

    print(f"Published to {published} client(s).")