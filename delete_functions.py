def delete_selection(market, selection_name):

    for selection in market["selections"]:

        if selection["name"] == selection_name:

            market["selections"].remove(selection)

            print("Selection deleted.")

            return
        
def delete_market(event, market_name):

    for market in event["markets"]:

        if market["name"] == market_name:

            event["markets"].remove(market)

            print("Market deleted.")

            return


def delete_event(platform, event_name):

    for event in platform:

        if event["event_name"] == event_name:

            platform.remove(event)

            print("Event deleted.")

            return