from display_functions import display_market
from history_functions import display_price_history
from pending_functions import (
    save_pending_changes,
    undo_pending_changes,
)
from actions.pricing_actions import handle_multiple_price_changes, edit_prices_for_market

from bets.liability_functions import display_market_liability

from workspace_display import display_market_workspace

from bets.settlement_functions import settle_market

from actions.market_status_actions import change_market_status

def open_market_workspace(platform, event, market, bets):

    while True:

        display_market_workspace(event, market, bets)

        print()
        print("MARKET WORKSPACE")
        print("================")
        print("E Edit Prices")
        print("S Save Pending")
        print("U Undo Pending")
        print("L Liability")
        print("T Settle Market")
        print("M Market Status")
        print("H Price History")
        print("0 Back")

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

        elif choice == "T":

            selection_number = int(input("Winning selection: "))

            winning_selection = market["selections"][selection_number - 1]["name"]

            settle_market(
                bets,
                event,
                market,
                winning_selection
            )

            print()
            print("✓ Market settled.")

            input("\nPress Enter to continue...")

        elif choice == "M":

            change_market_status(
                platform,
                market
            )

        elif choice == "0":

         break