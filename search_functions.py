def find_event(platform, event_name):

    for event in platform:

        if event["event_name"] == event_name:

            return event
    return None
        
def find_selection(event, market_name, selection_name):

    for market in event["markets"]:

        if market["name"] == market_name:

            for selection in market["selections"]:

                if selection["name"] == selection_name:

                    return selection