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

from save_load import save_platform

from reports.market_reports import display_market_report

from settings.market_settings import display_market_settings

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
        if market["status"] == "Closed":
            print("T Settle Market")
        print("H Price History")
        print("V Market Report")
        print("K Market Settings")
        print("0 Back")

        if market["status"] == "Trading":

            print("X Suspend Market")

        elif market["status"] == "Suspended":

            print("R Resume Trading")

        if market["status"] in ["Trading", "Suspended"]:

            print("C Close Market")

        if not market["published"]:

            print("P Publish Market")

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

            if market["status"] != "Closed":

                print()
                print("Market must be Closed before settlement.")

                input("\nPress Enter to continue...")

                continue

            selection_number = int(input("Winning selection: "))

            winning_selection = market["selections"][selection_number - 1]["name"]

            settle_market(
                platform,
                bets,
                event,
                market,
                winning_selection
            )

            print()
            print("✓ Market settled.")

            input("\nPress Enter to continue...")

        elif choice == "X":

            market["status"] = "Suspended"

            save_platform(platform)

            print()
            print("✓ Market suspended.")

            input("\nPress Enter to continue...")

        elif choice == "R":

            market["status"] = "Trading"

            save_platform(platform)

            print()
            print("✓ Market resumed.")

            input("\nPress Enter to continue...")

        elif choice == "C":

            market["status"] = "Closed"

            save_platform(platform)

            print()
            print("✓ Market closed.")

            input("\nPress Enter to continue...")

        elif choice == "V":

            display_market_report(
                bets,
                event,
                market
            )

        elif choice == "P":

            market["published"] = True

            save_platform(platform)

            print()
            print("✓ Market published.")

            input("\nPress Enter to continue...")

        elif choice == "K":

            display_market_settings(
                market
            )

        elif choice == "0":

         break