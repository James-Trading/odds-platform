from pricing import probability


def display_event(event):
    print(event["event_name"])
    print(event["category"], "-", event["class"], "-", event["type"])
    print()

    for market in event["markets"]:
        if market["displayed"]:
            display_market(market)


def display_market(market, numbered=False):
    published_status = "NOT PUBLISHED"

    if market["published"]:
        published_status = "PUBLISHED"

    print(
        "Market:",
        market["name"],
        market["status"],
        published_status
    )

    book_percentage = 0

    for i, selection in enumerate(market["selections"], start=1):
        if selection["displayed"] == False:
            continue
        
        top = selection["price"][0]
        bottom = selection["price"][1]

        calculation_price = selection["price"]

        if selection["pending_price"] is not None:

            calculation_price = selection["pending_price"]

        prob = probability(
            calculation_price[0],
            calculation_price[1]
        )

        if selection["active"]:
            book_percentage = book_percentage + prob

        status = "ACTIVE"

        if selection["active"] == False:
                status = "SUSPENDED"

        price_display = str(top) + "/" + str(bottom)

        if selection["pending_price"] is not None:

            pending_top = selection["pending_price"][0]
            pending_bottom = selection["pending_price"][1]

            price_display = (
                str(top) + "/" + str(bottom)
                + " -> "
                + str(pending_top) + "/" + str(pending_bottom)
                + " UNSAVED"
            )
        prefix = ""

        if numbered:

            prefix = f"{i}. "
        print(
            f"{prefix}{selection['name']} "
            f"{price_display} "
            f"{prob:.2f} % "
            f"{status} "
            f"{selection['result']}"
        )

    print("Book Percentage:", round(book_percentage, 2), "%")
    print()

def display_platform(platform):
    print("JAMES TRADING PLATFORM")
    print("======================")
    print()

    for event in platform:
        display_event(event)

def display_event_names(platform):

    print()

    for event in platform:

        print(event["event_name"])

def display_market_names(event):

    print()

    for market in event["markets"]:

        print(market["name"])

def display_selection_names(event, market_name):

    for market in event["markets"]:

        if market["name"] == market_name:

            print()

            for selection in market["selections"]:

                print(selection["name"])

def choose_event(platform):

    print()

    for index, event in enumerate(platform, start=1):
        print(index, event["event_name"])

    print()

    choice = int(input("Event number: "))

    return platform[choice - 1]

def choose_market(event):

    print()

    for index, market in enumerate(event["markets"], start=1):

        print(index, market["name"])

    print()

    choice = int(input("Market number: "))

    return event["markets"][choice - 1]

def choose_selection(market):

    print()

    for index, selection in enumerate(market["selections"], start=1):

        print(index, selection["name"])

    print()

    choice = int(input("Selection number: "))

    return market["selections"][choice - 1]