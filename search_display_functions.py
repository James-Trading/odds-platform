def display_selection_result(
        event_name,
        market_name,
        selection):

    print()

    print("EVENT:", event_name)
    print("MARKET:", market_name)
    print("SELECTION:", selection["name"])
    print("PRICE:",
          selection["price"][0],
          "/",
          selection["price"][1])
    status = "ACTIVE"

    if selection["active"] == False:
        status = "SUSPENDED"

    print("STATUS:", status)
    print("RESULT:", selection["result"])

def search_platform(
        platform,
        search_term):

    found = False

    for event in platform:

        if search_term.lower() in event["event_name"].lower():

            print()
            print("EVENT:", event["event_name"])
            print("CATEGORY:", event["category"], "-", event["class"], "-", event["type"])

            found = True

        for market in event["markets"]:

            if search_term.lower() in market["name"].lower():

                print()
                print("EVENT:", event["event_name"])
                print("MARKET:", market["name"])

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