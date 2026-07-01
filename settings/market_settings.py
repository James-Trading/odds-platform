def display_market_settings(market):

    print()
    print("MARKET SETTINGS")
    print("================")
    print()

    print(f"Published        {market['published']}")
    print(f"Status           {market['status']}")
    print(f"Max Win          £{market['limits']['max_win_per_customer']}")
    print(f"Max Liability    £{market['limits']['max_liability']}")

    print()
    print("Notes")
    print("-----")

    if market["notes"]:

        print(market["notes"])

    else:

        print("None")

    input("\nPress Enter to continue...")