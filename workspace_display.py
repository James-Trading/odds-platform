from bets.liability_functions import get_selection_liability
from display_functions import calculate_market_percentage

def display_market_workspace(event, market, bets):

    print()
    print("MARKET WORKSPACE")
    print("================")
    print(event["event_name"], "-", market["name"])
    print()

    print("No | Selection | Price | Win P/L")
    print("--------------------------------")

    for i, selection in enumerate(market["selections"], start=1):

        price = selection["price"]

        price_display = str(price[0]) + "/" + str(price[1])

        if selection["pending_price"] is not None:

            pending = selection["pending_price"]

            price_display = (
                price_display
                + " -> "
                + str(pending[0])
                + "/"
                + str(pending[1])
                + " UNSAVED"
            )

        liability = get_selection_liability(
            bets,
            event,
            market,
            selection
        )

        print(
            i,
            "|",
            selection["name"],
            "|",
            price_display,
            "|",
            f"£{liability:.2f}"
        )

    print()
    print(f"Book %: {calculate_market_percentage(market):.2f}")