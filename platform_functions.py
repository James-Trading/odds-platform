from search_functions import find_event, find_selection
from market_functions import suspend_market, unsuspend_market


def change_platform_price(platform,
                          event_name,
                          market_name,
                          selection_name,
                          new_price):

    event = find_event(platform, event_name)

    if event:

        selection = find_selection(
            event,
            market_name,
            selection_name
        )

        if selection:

            selection["price"] = new_price
        
            print("Price updated.")

        else:
            print("Selection not found.")

    else:
        print("Event not found.")

def suspend_platform_selection(platform,
                               event_name,
                               market_name,
                               selection_name):

    event = find_event(platform, event_name)

    if event:

        selection = find_selection(
            event,
            market_name,
            selection_name
        )

        if selection:

            selection["active"] = False

def suspend_platform_event(platform, event_name):

    event = find_event(platform, event_name)

    if event:

        for market in event["markets"]:

            market["status"] = "SUSPENDED"

            for selection in market["selections"]:

                selection["active"] = False

                print("Event suspended.")

    else:
        print("Event not found.")

def settle_platform_market(platform,
                           event_name,
                           market_name,
                           winner_name):

    event = find_event(platform, event_name)

    if event:

        for market in event["markets"]:

            if market["name"] == market_name:

                market["status"] = "SETTLED"

                for selection in market["selections"]:

                    selection["active"] = False

                    if selection["name"] == winner_name:
                        selection["result"] = "Winner"
                    else:
                        selection["result"] = "Loser"

            print("Market settled.")
    else:
        print("Event not found.")

def void_platform_market(platform,
                         event_name,
                         market_name):

    event = find_event(platform, event_name)

    if event:

        for market in event["markets"]:

            if market["name"] == market_name:

                market["status"] = "VOID"

                for selection in market["selections"]:

                    selection["active"] = False
                    selection["result"] = "Void"  

            print("Market voided.")
    else:
        print("Event not found.")   

def suspend_platform_market(
        platform,
        event_name,
        market_name):           
    event = find_event(platform, event_name)

    if event:

        for market in event["markets"]:

            if market["name"] == market_name:

                suspend_market(market)

                print("Market suspended.")   

def unsuspend_platform_market(
        platform,
        event_name,
        market_name):

    event = find_event(platform, event_name)

    if event:

        for market in event["markets"]:

            if market["name"] == market_name:

                unsuspend_market(market)

                print("Market unsuspended.")

def unsuspend_platform_selection(
        platform,
        event_name,
        market_name,
        selection_name):
    
    event = find_event(platform, event_name)

    if event:

        selection = find_selection(
        event,
        market_name,
        selection_name
        )

    if selection:

        selection["active"] = True

        print("Selection unsuspended.")

def unsuspend_platform_event(
        platform,
        event_name):

    event = find_event(platform, event_name)

    if event:

        for market in event["markets"]:

            market["status"] = "Active"

            for selection in market["selections"]:

                selection["active"] = True

        print("Event unsuspended.")