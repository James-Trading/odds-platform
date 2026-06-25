from display_functions import choose_event
from export_functions import export_event
from audit_functions import add_audit_log


def handle_export_event(platform):

    event = choose_event(platform)

    export_event(event)

    add_audit_log(
        f'{event["event_name"]} exported'
    )