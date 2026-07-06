def get_live_events(platform):

    events = []

    for event in platform:

        if event.get("live", False):

            events.append(event)

    return events