from event_functions import create_market, add_selection


def create_outright_market(event,
                           market_name,
                           runners):

    market = create_market(
        event,
        market_name
    )

    for runner_name, price in runners:

        add_selection(
            market,
            runner_name,
            price
        )

    return market