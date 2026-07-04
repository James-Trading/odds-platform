from reports.event_summary import display_event_summary

from workspaces.market_workspace import market_workspace


def event_workspace(event):

    while True:

        print()
        print("=" * 50)
        print(event["event_name"].upper())
        print("=" * 50)
        print()

        print("1 Event Summary")
        print("2 View Markets")
        print("3 Rename Event")
        print("4 Suspend Event")
        print("5 Unsuspend Event")
        print("6 Delete Event")
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

        elif choice == "0":

            break