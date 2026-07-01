def check_market_available(market):

    if market["status"] != "Trading":

        return False, f"Market is {market['status']}."

    if not market["published"]:

        return False, "Market is not published."

    return True, ""

def run_risk_checks(
    market,
):

    allowed, message = check_market_available(
        market
    )

    if not allowed:

        return False, message

    return True, ""