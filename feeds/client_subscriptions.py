from client_save_load import save_clients


def manage_client_subscriptions(clients, client, platform):

    print()
    print("CLIENT SUBSCRIPTIONS")
    print("====================")
    print()

    if client["subscriptions"] == []:
        print("No subscriptions.")
    else:
        for subscription in client["subscriptions"]:
            print(f"✓ {subscription}")

    print()
    print("A Add Subscription")
    print("R Remove Subscription")
    print("0 Back")

    choice = input("Choice: ").upper()

    if choice == "A":

        categories = []

        for event in platform:

            if event["category"] not in categories:

                categories.append(event["category"])

        print()
        print("AVAILABLE CATEGORIES")
        print("====================")

        for i, category in enumerate(categories, start=1):

            print(f"{i} {category}")

        category_number = int(input("Category number: "))

        category = categories[category_number - 1]

        if category not in client["subscriptions"]:

            client["subscriptions"].append(category)

            save_clients(clients)

            print()
            print(f"✓ {category} added.")

    elif choice == "R":

        for i, subscription in enumerate(client["subscriptions"], start=1):

            print(f"{i} {subscription}")

        subscription_number = int(input("Remove number: "))

        subscription = client["subscriptions"][subscription_number - 1]

        client["subscriptions"].remove(subscription)

        save_clients(clients)

        print()
        print(f"✓ {subscription} removed.")

    input("\nPress Enter to continue...")