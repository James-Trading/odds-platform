from workspaces.event_workspace import event_workspace


def choose_event(events):

    if len(events) == 0:

        print("\nNo events found.")
        input("\nPress Enter...")
        return

    print()
    print("EVENTS")
    print("======")
    print()

    for i, event in enumerate(events, start=1):

        print(f"{i}. {event['event_name']}")

    print()
    print("0 Back")

    choice = input("\nOpen event: ")

    if choice == "0":
        return

    try:

        event = events[int(choice) - 1]

        event_workspace(event)

    except (ValueError, IndexError):

        print("\nInvalid selection.")
        input("\nPress Enter...")