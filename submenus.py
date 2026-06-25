def show_main_menu():

    print()
    print("MAIN MENU")
    print("=========")
    print("1 Trading")
    print("2 Events")
    print("3 Clients")
    print("4 Audit")
    print("5 Exit")
    print()

    return input("Choice: ")


def show_trading_menu():

    print()
    print("TRADING")
    print("=======")
    print("1 Change Price")
    print("2 Suspend Selection")
    print("3 Suspend Market")
    print("4 Suspend Event")
    print("5 Unsuspend Selection")
    print("6 Unsuspend Market")
    print("7 Unsuspend Event")
    print("8 Settle Market")
    print("9 Void Market")
    print("10 Back")
    print()

    return input("Choice: ")


def show_events_menu():

    print()
    print("EVENTS")
    print("======")
    print("1 View Platform")
    print("2 View Event")
    print("3 Search")
    print("4 Create Event")
    print("5 Create Market")
    print("6 Create Selection")
    print("7 Create Template Event")
    print("8 Delete Selection")
    print("9 Delete Market")
    print("10 Delete Event")
    print("11 Back")
    print()

    return input("Choice: ")


def show_clients_menu():

    print()
    print("CLIENTS")
    print("=======")
    print("1 Add Client")
    print("2 View Clients")
    print("3 Back")
    print()

    return input("Choice: ")