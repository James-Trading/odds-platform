from workspaces.selection_workspace import selection_workspace

def market_workspace(event, market):

    while True:

        print()
        print("=" * 50)
        print(market["name"].upper())
        print("=" * 50)
        print()

        print(f"Event : {event['event_name']}")
        print(f"Selections : {len(market['selections'])}")
        print(f"Status : {market['status']}")
        print()

        print("1 View Selections")
        print("2 Edit Prices")
        print("3 Suspend Market")
        print("4 Publish Market")
        print("0 Back")

        choice = input("\nChoice: ")

        if choice == "1":

            print()
            print("SELECTIONS")
            print("==========")
            print()

            for i, selection in enumerate(market["selections"], start=1):

                price = f"{selection['price'][0]}/{selection['price'][1]}"

                status = "🟢"

                if not selection["active"]:
                    status = "🔴"

                print(f"{i}. {status} {selection['name']} ({price})")

            print()
            print("0 Back")

            selection_choice = input("\nChoose selection: ")

            if selection_choice == "0":
                continue

            try:

                selection = market["selections"][int(selection_choice) - 1]

                selection_workspace(
                    event,
                    market,
                    selection
                )

            except (ValueError, IndexError):

                print("\nInvalid selection.")
                input("\nPress Enter...")

        if choice == "0":
            break