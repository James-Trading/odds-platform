def send_price_update(client, event):

    feed = client.get("feed")

    connector = feed.get("connector", "None")

    print(f"Sending update via {connector} connector...")
    print(f"Client: {client['name']}")
    print(f"Event : {event['event_name']}")

    return True