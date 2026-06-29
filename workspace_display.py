from bets.liability_functions import get_selection_liability
from display_functions import calculate_market_percentage

def format_money(amount):

    if amount > 0:

        return f"+£{amount:.2f}"

    if amount < 0:

        return f"-£{abs(amount):.2f}"

    return "£0.00"

def format_money(amount):

    rounded = round(amount)

    if rounded > 0:
        return f"+£{rounded}"

    if rounded < 0:
        return f"-£{abs(rounded)}"

    return "£0"

def display_market_workspace(event, market, bets):

    print()
    print("MARKET WORKSPACE")
    print("================")
    print(event["event_name"], "-", market["name"])
    print(f"Status: {market['status']}")
    print()

    print(f"{'No':<3}{'Selection':<25}{'Price':<20}{'P/L':>12}")
    print("-" * 60)

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
            f"{i:<3}"
            f"{selection['name']:<25}"
            f"{price_display:<25}"
            f"{format_money(liability):>8}"
        )
    print()
    print(f"Book %: {calculate_market_percentage(market):.2f}")