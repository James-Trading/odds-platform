from save_load import save_platform


def change_market_status(platform, market):

    print()
    print("MARKET STATUS")
    print("=============")
    print()
    print(f"Current: {market['status']}")
    print()
    print("1 Trading")
    print("2 Suspended")
    print("3 Closed")
    print()

    choice = input("Choice: ")

    if choice == "1":
        new_status = "Trading"

    elif choice == "2":
        new_status = "Suspended"

    elif choice == "3":
        new_status = "Closed"

    else:
        return
    
    if market["status"] == new_status:

        print()
        print("Market already in that status.")

        input("\nPress Enter to continue...")

        return

    market["status"] = new_status

    save_platform(platform)

    print()
    print(f"✓ Market status changed to {market['status']}.")

    input("\nPress Enter to continue...")