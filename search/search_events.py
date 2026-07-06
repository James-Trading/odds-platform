from pickers.event_picker import choose_event


def search_events(platform):

    search_term = input("Search event: ").lower()

    matches = []

    for event in platform:

        if search_term in event["event_name"].lower():

            matches.append(event)

    choose_event(matches)
