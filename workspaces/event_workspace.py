from reports.event_summary import display_event_summary

from workspaces.market_workspace import market_workspace

from actions.creation_actions import handle_create_market

from state.app_state import mark_dirty

def event_workspace(event):

    while True:

        print()
        print("=" * 50)
        print(event["event_name"].upper())
        print("=" * 50)
        print()

        print("1 Event Summary")
        print("2 View Markets")
        print("3 Suspend Event")
        print("4 Unsuspend Event")
        print("5 Create Market")
        print("0 Back")

        choice = input("\nChoice: ")

        if choice == "1":

            display_event_summary(event)

            input("\nPress Enter...")

        elif choice == "2":

            print()
            print("MARKETS")
            print("=======")
            print()

            for i, market in enumerate(event["markets"], start=1):

                status = "🟢"

                if market["status"] != "Trading":
                    status = "🔴"

                print(f"{i}. {status} {market['name']}")

            print()
            print("0 Back")

            market_choice = input("\nChoose market: ")

            if market_choice == "0":
                continue

            try:

                market = event["markets"][int(market_choice) - 1]

                market_workspace(
                    event,
                    market
                )

            except (ValueError, IndexError):

                print("\nInvalid selection.")
                input("\nPress Enter...")

        elif choice == "3":

            event["active"] = False

            mark_dirty()

            print("\nEvent suspended.")
            input("\nPress Enter...")

        elif choice == "4":

            event["active"] = True

            mark_dirty()

            print("\nEvent unsuspended.")
            input("\nPress Enter...")

        elif choice == "5":

            handle_create_market([event])

        elif choice == "0":

            break