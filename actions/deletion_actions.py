from delete_functions import (
    delete_selection,
    delete_market,
    delete_event
)

from display_functions import (
    choose_event,
    choose_market,
    choose_selection,
    display_platform
)

from save_load import save_platform
from audit_functions import add_audit_log


def handle_delete_selection(platform):

    event = choose_event(platform)

    market = choose_market(event)

    selection = choose_selection(market)

    confirm = input("Are you sure? Y/N: ")

    if confirm.upper() == "Y":

        delete_selection(
            market,
            selection["name"]
        )

        add_audit_log(
            f'{selection["name"]} deleted from {event["event_name"]} / {market["name"]}'
        )

        save_platform(platform)

        display_platform(platform)


def handle_delete_market(platform):

    event = choose_event(platform)

    market = choose_market(event)

    confirm = input("Are you sure? Y/N: ")

    if confirm.upper() == "Y":

        delete_market(
            event,
            market["name"]
        )

        add_audit_log(
            f'{market["name"]} deleted from {event["event_name"]}'
        )

        save_platform(platform)

        display_platform(platform)


def handle_delete_event(platform):

    event = choose_event(platform)

    confirm = input("Are you sure? Y/N: ")

    if confirm.upper() == "Y":

        delete_event(
            platform,
            event["event_name"]
        )

        add_audit_log(
            f'{event["event_name"]} deleted'
        )

        save_platform(platform)

        display_platform(platform)