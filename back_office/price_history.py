from display_functions import choose_event
from pickers.market_picker import pick_market
from pickers.selection_picker import choose_selection


def display_price_history(platform):

    event = choose_event(platform)

    if event is None:
        return

    market = pick_market(event)

    if market is None:
        return

    print()
    print("=" * 50)
    print("PRICE HISTORY")
    print("=" * 50)

    for selection in market.get("selections", []):

        print()
        print("=" * 50)
        print(selection["name"])
        print("-" * 50)

        history = selection.get("price_history", [])

        if history == []:

            print("No price history.")

        else:

            for item in history:

                print(f"Time : {item['created']}")

                if "old_price" in item:
                    print(f"Price: {item['old_price'][0]}/{item['old_price'][1]}  ->  {item['new_price'][0]}/{item['new_price'][1]}")
                else:
                    print(f"Opened at {item['price'][0]}/{item['price'][1]}")

                print()

    input("\nPress Enter...")