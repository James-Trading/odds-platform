from datetime import datetime
def save_pending_changes(market):

    changes = 0

    for selection in market["selections"]:

        if selection["pending_price"] is not None:

            old_price = selection["price"]
            new_price = selection["pending_price"]

            selection["price_history"].append(
                {
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "price": new_price
                }
            )

            selection["price"] = new_price

            selection["pending_price"] = None

            changes += 1

    print(f"{changes} pending change(s) saved.")