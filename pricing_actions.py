from display_functions import choose_event, choose_market, choose_selection
from platform_functions import change_platform_price
from save_load import save_platform
from display_functions import display_platform
from audit_functions import add_audit_log


def handle_price_change(platform):

    event = choose_event(platform)

    market = choose_market(event)

    selection = choose_selection(market)

    top = int(input("Numerator: "))
    bottom = int(input("Denominator: "))

    change_platform_price(
        platform,
        event["event_name"],
        market["name"],
        selection["name"],
        (top, bottom)
    )

    add_audit_log(
        f'{selection["name"]} in {event["event_name"]} / {market["name"]} changed to {top}/{bottom}'
    )

    save_platform(platform)

    display_platform(platform)