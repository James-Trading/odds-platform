def save_pending_changes(market):

    changes = 0

    for selection in market["selections"]:

        if selection["pending_price"] is not None:

            selection["price"] = selection["pending_price"]

            selection["pending_price"] = None

            changes += 1

    print(f"{changes} pending change(s) saved.")