def display_bet_ticker(bets):

    print()
    print("BET TICKER")
    print("==========")
    print()

    print("1 All Bets")
    print("2 Filter by Event")
    print()

    choice = input("Choice: ")

    filtered_bets = bets

    if choice == "2":

        event_name = input("Event name: ")

        filtered_bets = []

        for bet in bets:

            if event_name.lower() in bet["event"].lower():

                filtered_bets.append(bet)

    latest_bets = sorted(
        filtered_bets,
        key=lambda bet: bet["created"],
        reverse=True
    )

    latest_bets = latest_bets[:10]

    for bet in latest_bets:

        time = bet["created"][11:]

        top = bet["price"][0]
        bottom = bet["price"][1]

        print(
            f"{time:<8} "
            f"{bet['client']:<15} "
            f"{bet['event']:<30} "
            f"{bet['selection']:<25} "
            f"£{round(bet['stake']):<6} "
            f"{top}/{bottom}"
        )

    input("\nPress Enter to continue...")