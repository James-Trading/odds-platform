def get_live_events(platform):

    return [
        event
        for event in platform
        if event.get("live", False)
    ]


def get_published_events(platform):

    return [
        event
        for event in platform
        if event.get("published", False)
    ]


def get_suspended_events(platform):

    return [
        event
        for event in platform
        if not event.get("active", True)
    ]


def get_upcoming_events(platform):

    return platform