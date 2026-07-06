from price_engine.price_ladder import (
    set_price,
    shorten_one_tick,
    lengthen_one_tick
)

from state.app_state import is_dirty, mark_dirty

def selection_workspace(event, market, selection):

    while True:

        print()
        print("=" * 50)
        print(selection["name"].upper())
        print("=" * 50)
        print()

        print(f"Event  : {event['event_name']}")
        print(f"Market : {market['name']}")

        price = f"{selection['price'][0]}/{selection['price'][1]}"

        print()
        print(f"Price  : {price}")

        if selection["active"]:
            print("Status : ACTIVE")
        else:
            print("Status : SUSPENDED")

        if is_dirty():
            print("Saved  : NO - UNSAVED CHANGES")
        else:
            print("Saved  : YES")

        print()
        print("-" * 50)
        print("1 Shorten One Tick")
        print("2 Lengthen One Tick")
        print("3 Type New Price")
        print("-" * 50)
        print("4 Suspend Selection")
        print("5 Unsuspend Selection")
        print("-" * 50)
        print("6 Settle Winner")
        print("7 Void Selection")
        print("-" * 50)
        print("0 Back")

        choice = input("\nChoice: ")

        if choice == "1":

            shorten_one_tick(selection)

            print("\nPrice shortened one tick.")
            input("\nPress Enter...")

        elif choice == "2":

            lengthen_one_tick(selection)

            print("\nPrice lengthened one tick.")
            input("\nPress Enter...")

        elif choice == "3":

            print()
            print(f"Current price: {selection['price'][0]}/{selection['price'][1]}")

            new_price = input("New price: ")

            numerator, denominator = new_price.split("/")

            set_price(
                selection,
                int(numerator),
                int(denominator)
            )

            print("\nPrice updated.")
            input("\nPress Enter...")

        elif choice == "4":

            selection["active"] = False

            print("\nSelection suspended.")
            input("\nPress Enter...")

        elif choice == "5":

            selection["active"] = True

            print("\nSelection unsuspended.")
            input("\nPress Enter...")

        elif choice == "6":

            confirm = input("Set this selection as winner? (y/n): ").lower()

            if confirm == "y":

                for runner in market["selections"]:

                    if runner == selection:
                        runner["result"] = "winner"
                    else:
                        runner["result"] = "loser"

                mark_dirty()

                print("\nMarket settled.")
                input("\nPress Enter...")

        if choice == "0":
            break