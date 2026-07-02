from logs.feed_log import log_feed_update

def publish_market_prices(clients, event):

    print()
    print("PUBLISHING MARKET")
    print("=================")
    print()

    published = 0

    for client in clients:

        if event["event_name"] not in client["booked_events"]:
            continue

        feed = client.get("feed")

        if not feed:
            continue

        if not feed["enabled"]:
            continue

        print(f"✓ {client['name']} updated.")

        log_feed_update(
            client["name"],
            event["event_name"]
        )

        published += 1

    print()
    print(f"{published} client(s) updated.")

    input("\nPress Enter to continue...")