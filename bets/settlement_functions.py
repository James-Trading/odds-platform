from bets.bet_save_load import save_bets

from save_load import save_platform


def settle_market(
    platform,
    bets,
    event,
    market,
    winning_selection,
):

    for bet in bets:

        if bet["status"] != "Open":
            continue

        if bet["event"] != event["event_name"]:
            continue

        if bet["market"] != market["name"]:
            continue

        if bet["selection"] == winning_selection:

            bet["status"] = "Closed"
            bet["settled"] = True
            bet["result"] = "Won"

        else:

            bet["status"] = "Closed"
            bet["settled"] = True
            bet["result"] = "Lost"

    market["status"] = "Settled"

    save_platform(platform)

    save_bets(bets)