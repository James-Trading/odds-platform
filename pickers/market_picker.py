def pick_market(event):

    markets = event.get("markets", [])

    if len(markets) == 0:

        print("\nNo markets found.")
        input("\nPress Enter...")
        return None

    print()
    print("MARKETS")
    print("=======")
    print()

    for i, market in enumerate(markets, start=1):

        print(f"{i}. {market['name']}")

    print()
    print("0 Back")

    choice = input("\nChoose market: ")

    if choice == "0":
        return None

    try:

        return markets[int(choice) - 1]

    except (ValueError, IndexError):

        print("\nInvalid selection.")
        input("\nPress Enter...")
        return None