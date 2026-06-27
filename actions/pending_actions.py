from display_functions import (
    choose_event,
    choose_market,
    display_platform
)

from pending_functions import save_pending_changes, undo_pending_changes
from save_load import save_platform
from audit_functions import add_audit_log

def handle_undo_pending_changes(platform):

    event = choose_event(platform)

    market = choose_market(event)

    undo_pending_changes(market)

    save_platform(platform)

    display_platform(platform)

def handle_save_pending_changes(platform):

    event = choose_event(platform)

    market = choose_market(event)

    save_pending_changes(market)

    add_audit_log(
        f'Pending changes saved for {event["event_name"]} / {market["name"]}'
    )

    save_platform(platform)

    display_platform(platform)