from publish_functions import publish_event
from display_functions import choose_event
from audit_functions import add_audit_log


def handle_publish_event(clients, platform):

    event = choose_event(platform)

    publish_event(
        clients,
        event
    )

    add_audit_log(
        f'{event["event_name"]} published'
    )