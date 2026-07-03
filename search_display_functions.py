def display_selection_result(
        event_name,
        market_name,
        selection):

    print()
    print("SELECTION MATCH")
    print("===============")

    print(f"Event     : {event_name}")
    print(f"Market    : {market_name}")
    print(f"Selection : {selection['name']}")

    print(
        "Price     :",
        selection["price"][0],
        "/",
        selection["price"][1]
    )

    status = "ACTIVE"

    if selection["active"] == False:
        status = "SUSPENDED"

    print(f"Status    : {status}")
    print(f"Result    : {selection.get('result', 'Not settled')}")

def search_platform(
        platform,
        search_term):

    found = False

    for event in platform:

        if search_term.lower() in event["event_name"].lower():

            print()
            print("MARKET MATCH")
            print("============")
            print(f"Event  : {event['event_name']}")
            print(f"Market : {market['name']}")

            found = True

        for market in event["markets"]:

            if search_term.lower() in market["name"].lower():

                print()
                print("EVENT MATCH")
                print("===========")
                print(f"Event    : {event['event_name']}")
                print(f"Category : {event['category']} - {event['class']} - {event['type']}")

                found = True

            for selection in market["selections"]:

                if search_term.lower() in selection["name"].lower():

                    display_selection_result(
                        event["event_name"],
                        market["name"],
                        selection
                    )

                    found = True

    if found == False:

        print("No results found.")