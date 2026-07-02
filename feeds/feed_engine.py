from logs.feed_log import log_feed_update

from audit_functions import add_audit_log

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

        add_audit_log(
            f"Prices distributed to {client['name']} for {event['event_name']}"
        )

        log_feed_update(
            client["name"],
            event["event_name"]
        )

        published += 1

    print()
    print(f"{published} client(s) updated.")

    input("\nPress Enter to continue...")