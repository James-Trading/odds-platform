def add_published_to_existing_markets(platform):

    for event in platform:

        for market in event["markets"]:

            if "published" not in market:

                market["published"] = False

    print("Migration complete.")

def add_pending_price_to_existing_selections(platform):

    for event in platform:

        for market in event["markets"]:

            for selection in market["selections"]:

                if "pending_price" not in selection:

                    selection["pending_price"] = None

    print("Pending price migration complete.")