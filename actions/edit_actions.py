from display_functions import choose_event
from save_load import save_platform
from audit_functions import add_audit_log
from edit_functions import (
    edit_event_name,
    edit_event_start_time,
    edit_event_suspend_mode,
    edit_event_status
)


def handle_edit_event_name(platform):

    event = choose_event(platform)

    old_name = event["event_name"]

    edit_event_name(event)

    if old_name != event["event_name"]:

        add_audit_log(
            f'Event renamed from "{old_name}" to "{event["event_name"]}"'
        )

        save_platform(platform)

def handle_edit_event(platform):

    event = choose_event(platform)

    print()
    print("EDIT EVENT")
    print("==========")
    print("1 Event Name")
    print("2 Start Time")
    print("3 Suspend Mode")
    print("4 Status")

    choice = input("Choice: ")

    old_event = event.copy()

    if choice == "1":

        edit_event_name(event)

    elif choice == "2":

        edit_event_start_time(event)

    elif choice == "3":

        edit_event_suspend_mode(event)

    elif choice == "4":

        edit_event_status(event)

    add_audit_log(
        f'{event["event_name"]} edited'
    )

    save_platform(platform)