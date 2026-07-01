from client_save_load import save_clients

def display_client_feed(clients, client):

    print()
    print("CLIENT FEED")
    print("===========")
    print()

    print(f"Client              {client['name']}")
    print(f"Status              {client['status']}")

    feed = client.get("feed")

    if feed:

        print(f"Feed Enabled        {feed['enabled']}")
        print(f"Connector           {feed['connector']}")
        print(f"Last Price Update   {feed['last_price_update']}")
        print(f"Last Bet Received   {feed['last_bet_received']}")

    else:

        print("Feed not configured.")

    print()
    print("1 Toggle Feed")
    print("2 Change Risk Mode")
    print("0 Back")

    choice = input("\nChoice: ")

    if choice == "1":

        if feed:

            feed["enabled"] = not feed["enabled"]

            save_clients(clients)

            print()

            print("Feed updated.")

            input("\nPress Enter to continue...")