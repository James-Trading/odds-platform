def display_bets(bets):

    print()
    print("OPEN BETS")
    print("=" * 80)

    if not bets:

        print("No bets.")

        return

    for bet in bets:

        price = f"{bet['price'][0]}/{bet['price'][1]}"

        print(
            f"{bet['client']} | "
            f"{bet['selection']} | "
            f"£{bet['stake']} @ {price}"
        )