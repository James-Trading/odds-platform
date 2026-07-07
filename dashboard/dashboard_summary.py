from state.app_state import is_dirty


def count_markets(platform):

    total = 0

    for event in platform:
        total += len(event.get("markets", []))

    return total


def count_selections(platform):

    total = 0

    for event in platform:

        for market in event.get("markets", []):
            total += len(market.get("selections", []))

    return total


def count_suspended_events(platform):

    return len([
        event
        for event in platform
        if not event.get("active", True)
    ])


def count_suspended_markets(platform):

    total = 0

    for event in platform:

        for market in event.get("markets", []):

            if not market.get("active", True):
                total += 1

    return total


def count_unpublished_markets(platform):

    total = 0

    for event in platform:

        for market in event.get("markets", []):

            if not market.get("published", False):
                total += 1

    return total


def display_dashboard(platform):

    print()
    print("=" * 50)
    print("ODDS PLATFORM v0.5")
    print("=" * 50)
    print()

    print(f"Events              : {len(platform)}")
    print(f"Markets             : {count_markets(platform)}")
    print(f"Selections          : {count_selections(platform)}")
    print()
    print(f"Suspended Events    : {count_suspended_events(platform)}")
    print(f"Suspended Markets   : {count_suspended_markets(platform)}")
    print(f"Unpublished Markets : {count_unpublished_markets(platform)}")

    if is_dirty():
        print("Unsaved Changes     : YES")
    else:
        print("Unsaved Changes     : NO")

    print()