def display_price_history(selection):

    print()
    print("PRICE HISTORY")
    print("=============")
    print(selection["name"])
    print()

    if selection["price_history"] == []:

        print("No price history.")

        return

    print("Created              Price")
    print("--------------------------")

    for entry in reversed(selection["price_history"][-20:]):

        price = (
            str(entry["price"][0])
            + "/"
            + str(entry["price"][1])
        )

        print(
            entry["created"],
            price
        )