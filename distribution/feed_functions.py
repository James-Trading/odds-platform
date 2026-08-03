def format_fractional_price(price):
    if (
        isinstance(price, (list, tuple))
        and len(price) == 2
    ):
        return f"{price[0]}/{price[1]}"

    return str(price)


def get_selection_status(selection, market):
    result = selection.get("result", "")

    if result:
        return result

    market_is_suspended = (
        str(market.get("status", "ACTIVE")).upper()
        == "SUSPENDED"
    )

    if market_is_suspended:
        return "Suspended"

    if not selection.get("active", True):
        return "Suspended"

    return "Active"


def get_published_events(platform):
    customer_events = []

    for event in platform:
        if not event.get("published", False):
            continue

        customer_event = {
            "id": event.get("id"),
            "name": event.get(
                "event_name",
                "Unnamed Event",
            ),
            "category": event.get("category"),
            "class": event.get("class"),
            "type": event.get("type"),
            "start_time": event.get("start_time"),
            "status": event.get("status"),
            "markets": [],
        }

        for market in event.get("markets", []):
            # Hidden markets must not leave the platform.
            if not market.get("displayed", True):
                continue

            customer_market = {
                "id": market.get("id"),
                "name": market.get(
                    "name",
                    "Unnamed Market",
                ),
                "status": market.get(
                    "status",
                    "ACTIVE",
                ),
                "selections": [],
            }

            for selection in market.get(
                "selections",
                [],
            ):
                # Hidden selections must not appear
                # in a customer feed.
                if not selection.get(
                    "displayed",
                    True,
                ):
                    continue

                customer_market[
                    "selections"
                ].append(
                    {
                        "id": selection.get("id"),
                        "name": selection.get(
                            "name",
                            "Unnamed Selection",
                        ),
                        "price": (
                            format_fractional_price(
                                selection.get(
                                    "price",
                                    [0, 1],
                                )
                            )
                        ),
                        "status": (
                            get_selection_status(
                                selection,
                                market,
                            )
                        ),
                        "result": selection.get(
                            "result",
                            "",
                        ),
                    }
                )

            customer_event["markets"].append(
                customer_market
            )

        customer_events.append(customer_event)

    return customer_events

def get_client_feed(platform, client):
    if client.get("status", "").lower() != "active":
        return []

    feed_settings = client.get("feed", {})

    if not feed_settings.get("enabled", False):
        return []

    published_events = get_published_events(platform)

    booked_events = {
        str(event_name).strip().lower()
        for event_name in client.get("booked_events", [])
    }

    subscriptions = {
        str(category).strip().lower()
        for category in client.get("subscriptions", [])
    }

    client_events = []

    for event in published_events:
        event_name = str(event.get("name", "")).strip().lower()
        event_category = str(event.get("category", "")).strip().lower()

        is_booked = event_name in booked_events
        is_subscribed = event_category in subscriptions

        if not is_booked and not is_subscribed:
            continue

        client_events.append(event)

    return client_events