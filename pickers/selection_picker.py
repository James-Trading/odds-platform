from workspaces.selection_workspace import selection_workspace


def choose_selection(matches):

    if len(matches) == 0:

        print("\nNo selections found.")
        input("\nPress Enter...")
        return

    print()
    print("SELECTION RESULTS")
    print("=================")
    print()

    for i, match in enumerate(matches, start=1):

        event = match["event"]
        market = match["market"]
        selection = match["selection"]

        price = f"{selection['price'][0]}/{selection['price'][1]}"

        print(
            f"{i}. {event['event_name']} > "
            f"{market['name']} > "
            f"{selection['name']} ({price})"
        )

    print()
    print("0 Back")

    choice = input("\nOpen selection: ")

    if choice == "0":
        return

    try:

        match = matches[int(choice) - 1]

        selection_workspace(
            match["event"],
            match["market"],
            match["selection"]
        )

    except (ValueError, IndexError):

        print("\nInvalid selection.")
        input("\nPress Enter...")