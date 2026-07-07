from pickers.selection_picker import choose_selection

from workspaces.event_workspace import event_workspace
from workspaces.market_workspace import market_workspace
from workspaces.selection_workspace import selection_workspace

def global_search(platform, clients):

    search_term = input("Global search: ").lower()

    print()
    print("=" * 50)
    print("GLOBAL SEARCH")
    print("=" * 50)
    print()

    found = False
    results = []

    print("EVENTS")
    print("-" * 50)

    for event in platform:

        if search_term in event["event_name"].lower():

            results.append(("event", event))

            print(f"{len(results)}. {event['event_name']}")

            found = True

    print()
    print("MARKETS")
    print("-" * 50)

    for event in platform:

        for market in event.get("markets", []):

            if search_term in market["name"].lower():

                results.append(("market", event, market))

                print(
                    f"{len(results)}. "
                    f"{event['event_name']} > "
                    f"{market['name']}"
                )

                found = True

    print()
    print("EVENTS")
    print("-" * 50)

    for event in platform:

        if search_term in event["event_name"].lower():

            print(event["event_name"])
            found = True

    print()
    print("MARKETS")
    print("-" * 50)

    for event in platform:

        for market in event.get("markets", []):

            if search_term in market["name"].lower():

                print(f"{event['event_name']} > {market['name']}")

                found = True

    print()
    print("SELECTIONS")
    print("-" * 50)

    selection_matches = []

    for event in platform:

        for market in event.get("markets", []):

            for selection in market.get("selections", []):

                if search_term in selection["name"].lower():

                    results.append(("selection", event, market, selection))

                    price = f"{selection['price'][0]}/{selection['price'][1]}"

                    print(
                        f"{len(results)}. "
                        f"{event['event_name']} > "
                        f"{market['name']} > "
                        f"{selection['name']} ({price})"
                    )

                    found = True

    if len(selection_matches) > 0:

        choose_selection(selection_matches)

        return

    print()
    print("CLIENTS")
    print("-" * 50)

    for client in clients:

        if search_term in client.get("name", "").lower():

            print(f"- {client.get('name')}")
            found = True

    if not found:

        print()
        print("No results found.")

    if found:

        print()

        choice = input("Open result (0 to cancel): ")

        if choice != "0":

            result = results[int(choice) - 1]

            if result[0] == "event":

                event_workspace(result[1])

            elif result[0] == "market":

                market_workspace(
                    result[1],
                    result[2]
                )

            elif result[0] == "selection":

                selection_workspace(
                    result[1],
                    result[2],
                    result[3]
                )

    input("\nPress Enter...")