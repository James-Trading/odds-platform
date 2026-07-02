def manage_client_subscriptions(client):

    print()
    print("CLIENT SUBSCRIPTIONS")
    print("====================")
    print()

    if client["subscriptions"] == []:

        print("No subscriptions.")

    else:

        for subscription in client["subscriptions"]:

            print(f"✓ {subscription}")

    input("\nPress Enter to continue...")