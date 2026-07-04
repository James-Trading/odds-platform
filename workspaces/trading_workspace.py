def trading_workspace():

    while True:

        print()
        print("=" * 50)
        print("TRADING")
        print("=" * 50)
        print()

        print("1 Search")
        print("2 Upcoming Events")
        print("3 Live Events")
        print("4 Published Events")
        print("5 Suspended Events")
        print("0 Back")

        choice = input("\nChoice: ")

        if choice == "0":
            break