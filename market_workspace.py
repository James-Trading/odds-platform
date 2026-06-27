from display_functions import display_market
from history_functions import display_price_history
from pending_functions import (
    save_pending_changes,
    undo_pending_changes,
)
from actions.pricing_actions import handle_multiple_price_changes, edit_prices_for_market

from bets.liability_functions import display_market_liability

def open_market_workspace(event, market, bets):

    while True:

        display_market(market, numbered=True)

        print()
        print("MARKET WORKSPACE")
        print("================")
        print("E Edit Prices")
        print("S Save Pending")
        print("U Undo Pending")
        print("H Price History")
        print("0 Back")
        print("L Liability")

        choice = input("Choice: ").upper()

        if choice == "E":

            edit_prices_for_market(market)

        elif choice == "S":

                save_pending_changes(market)

                print()
                print("✓ Pending changes saved.")

                input("\nPress Enter to continue")

        elif choice == "U":

                undo_pending_changes(market)

                print()
                print("✓ Pending changes reverted.")

                input("\nPress Enter to continue()")

        elif choice == "H":

                selection_number = int(input("Selection: "))

                selection = market["selections"][selection_number - 1]

                display_price_history(selection)

                input("\nPress Enter to continue()")

        elif choice == "L":

            display_market_liability(
                bets,
                event,
                market
            )

            input("\nPress Enter to continue...")

        elif choice == "0":

         break