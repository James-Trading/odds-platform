from search.search_events import search_events

from pickers.event_picker import choose_event
from filters.event_filters import (
    get_upcoming_events,
    get_live_events,
    get_published_events,
    get_suspended_events
)

from actions.creation_actions import handle_create_event

def trading_workspace(platform, clients):

    while True:

        print()
        print("=" * 50)
        print("TRADING")
        print("=" * 50)
        print()

        print("1 Search")
        print("2 Upcoming Events")
        print("3 Live Events")
        print("4 Published Events")
        print("5 Suspended Events")
        print("6 Create Event")
        print("0 Back")

        choice = input("\nChoice: ")

        if choice == "1":

            search_events(platform)

            input("\nPress Enter...")

        elif choice == "2":

            events = get_upcoming_events(platform)
            choose_event(events)

        elif choice == "3":

            events = get_live_events(platform)
            choose_event(events)

        elif choice == "4":

            events = get_published_events(platform)
            choose_event(events)

        elif choice == "5":

            events = get_suspended_events(platform)
            choose_event(events)

        elif choice == "6":

            handle_create_event(
                platform,
                clients
            )

        if choice == "0":
            break