from display_functions import (
    choose_event,
    choose_market,
    choose_selection
)

from actions.client_actions import choose_client
from bets.bet_functions import add_bet

from risk.risk_checks import run_risk_checks


def handle_create_bet(bets, clients, platform):

    client = choose_client(clients)

    if client is None:

        return

    event = choose_event(platform)

    market = choose_market(event)

    allowed, message = run_risk_checks(
        market
    )

    if not allowed:

        print()
        print(message)

        input("\nPress Enter to continue...")

        return

    selection = choose_selection(market)

    print()
    print("CREATE BET")
    print("==========")
    print(f"Client: {client['name']}")
    print(f"Event: {event['event_name']}")
    print(f"Market: {market['name']}")
    print(f"Selection: {selection['name']}")

    price = selection["price"]

    print(f"Price: {price[0]}/{price[1]}")

    stake = float(input("Stake: "))

    add_bet(
        bets,
        client["name"],
        event["event_name"],
        market["name"],
        selection["name"],
        stake,
        price,
        event["id"],
        market["id"],
        selection["id"]

    )