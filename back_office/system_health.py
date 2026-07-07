from dashboard.dashboard_summary import (
    count_markets,
    count_selections,
    count_suspended_events,
    count_suspended_markets,
    count_unpublished_markets
)

from state.app_state import is_dirty


def count_audit_entries():

    try:

        with open("audit_log.txt", "r") as file:
            return len(file.readlines())

    except FileNotFoundError:

        return 0


def display_system_health(platform, clients):

    print()
    print("=" * 50)
    print("SYSTEM HEALTH")
    print("=" * 50)
    print()

    print("PLATFORM")
    print("-" * 50)
    print(f"Events              : {len(platform)}")
    print(f"Markets             : {count_markets(platform)}")
    print(f"Selections          : {count_selections(platform)}")
    print(f"Clients             : {len(clients)}")
    print()

    print(f"Suspended Events    : {count_suspended_events(platform)}")
    print(f"Suspended Markets   : {count_suspended_markets(platform)}")
    print(f"Unpublished Markets : {count_unpublished_markets(platform)}")
    print()

    if is_dirty():
        print("Unsaved Changes     : YES")
    else:
        print("Unsaved Changes     : NO")

    print()
    print("LOGS")
    print("-" * 50)
    print(f"Audit Entries       : {count_audit_entries()}")

    print()
    print("=" * 50)