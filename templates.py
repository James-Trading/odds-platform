from event_functions import create_event, create_market, add_selection


def create_eurovision_template(event_name):

    event = create_event(
        "SPECIALS",
        "Music Specials",
        "Eurovision",
        event_name
    )

    create_market(event, "Winner")
    create_market(event, "Top 3")
    create_market(event, "Top 5")

    return event


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

def create_strictly_template(event_name):

    event = create_event(
        "SPECIALS",
        "TV Specials",
        "Strictly Come Dancing",
        event_name
    )

    create_market(event, "Outright")
    create_market(event, "Top 3 Finish")
    create_market(event, "Top Male")
    create_market(event, "Top Female")
    create_market(event, "Next Elimination")

    return event