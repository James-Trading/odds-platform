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

    for event in platform:

        for market in event["markets"]:

            for selection in market["selections"]:

                if search_term.lower() in selection["name"].lower():

                    display_selection_result(
                        event["event_name"],
                        market["name"],
                        selection
                    )