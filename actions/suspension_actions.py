from display_functions import (
    choose_event,
    choose_market,
    choose_selection,
    display_platform
)

from platform_functions import (
    suspend_platform_selection,
    suspend_platform_event,
    suspend_platform_market,
    unsuspend_platform_selection,
    unsuspend_platform_market,
    unsuspend_platform_event
)

from save_load import save_platform
from audit_functions import add_audit_log


def handle_suspend_selection(platform):
    event = choose_event(platform)
    market = choose_market(event)
    selection = choose_selection(market)

    suspend_platform_selection(
        platform,
        event["event_name"],
        market["name"],
        selection["name"]
    )

    add_audit_log(
        f'{selection["name"]} suspended in {event["event_name"]} / {market["name"]}'
    )

    save_platform(platform)
    display_platform(platform)


def handle_suspend_event(platform):
    event = choose_event(platform)

    suspend_platform_event(
        platform,
        event["event_name"]
    )

    add_audit_log(
        f'{event["event_name"]} suspended'
    )

    save_platform(platform)
    display_platform(platform)


def handle_suspend_market(platform):
    event = choose_event(platform)
    market = choose_market(event)

    suspend_platform_market(
        platform,
        event["event_name"],
        market["name"]
    )

    add_audit_log(
        f'{market["name"]} suspended in {event["event_name"]}'
    )

    save_platform(platform)
    display_platform(platform)


def handle_unsuspend_selection(platform):
    event = choose_event(platform)
    market = choose_market(event)
    selection = choose_selection(market)

    unsuspend_platform_selection(
        platform,
        event["event_name"],
        market["name"],
        selection["name"]
    )

    add_audit_log(
        f'{selection["name"]} unsuspended in {event["event_name"]} / {market["name"]}'
    )

    save_platform(platform)
    display_platform(platform)


def handle_unsuspend_market(platform):
    event = choose_event(platform)
    market = choose_market(event)

    unsuspend_platform_market(
        platform,
        event["event_name"],
        market["name"]
    )

    add_audit_log(
        f'{market["name"]} unsuspended in {event["event_name"]}'
    )

    save_platform(platform)
    display_platform(platform)


def handle_unsuspend_event(platform):
    event = choose_event(platform)

    unsuspend_platform_event(
        platform,
        event["event_name"]
    )

    add_audit_log(
        f'{event["event_name"]} unsuspended'
    )

    save_platform(platform)
    display_platform(platform)