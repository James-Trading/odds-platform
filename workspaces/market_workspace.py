from workspaces.selection_workspace import selection_workspace

from actions.creation_actions import handle_create_selection

from state.app_state import mark_dirty

def market_workspace(event, market):

    while True:

        print()
        print("=" * 50)
        print(market["name"].upper())
        print("=" * 50)
        print()

        print(f"Event : {event['event_name']}")
        print(f"Selections : {len(market['selections'])}")
        if market.get("active", True):
            print("Status : ACTIVE")
        else:
            print("Status : SUSPENDED")
        print()

        print("1 View Selections")
        print("2 Edit Prices")
        print("-" * 50)
        print("3 Suspend Market")
        print("4 Unsuspend Market")
        print("-" * 50)
        print("5 Create Selection")
        print("-" * 50)
        print("6 Publish Market")
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

        elif choice == "2":

            print("\nUse 'View Selections' then choose a selection to change prices.")
            input("\nPress Enter...")

        elif choice == "3":

            market["active"] = False

            mark_dirty()

            print("\nMarket suspended.")
            input("\nPress Enter...")

        elif choice == "4":

            market["active"] = True

            mark_dirty()

            print("\nMarket unsuspended.")
            input("\nPress Enter...")

        elif choice == "5":

            handle_create_selection([event])

        elif choice == "6":

            market["published"] = True

            mark_dirty()

            print("\nMarket published.")
            input("\nPress Enter...")

        if market.get("published", False):
            print("Published : YES")
        else:
            print("Published : NO")

        if choice == "0":
            break