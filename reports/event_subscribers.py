def display_event_subscribers(clients, event):

    print()
    print("EVENT SUBSCRIBERS")
    print("=================")
    print()

    count = 0

    for client in clients:

        if event["event_name"] in client["booked_events"]:

            print(f"✓ {client['name']}")

            count += 1

    print()
    print(f"Total Subscribers: {count}")

    input("\nPress Enter to continue...")