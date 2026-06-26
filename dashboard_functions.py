from datetime import datetime
def display_dashboard(platform, clients):

    event_count = len(platform)

    market_count = 0
    selection_count = 0
    pending_count = 0

    published_market_count = 0
    suspended_market_count = 0
    events_today_count = 0

    today_events = []

    action_items = []

    for event in platform:

        if event["start_time"] != "":

            try:

                start = datetime.strptime(
                    event["start_time"],
                    "%d/%m/%Y %H:%M"
                )

                if start.date() == datetime.now().date():

                    events_today_count += 1
                
                    today_events.append(
                        (
                            start.strftime("%H:%M"),
                            event["event_name"]
                        )
                    )

            except ValueError:

                pass

        for market in event["markets"]:

            market_count += 1

            if market["published"]:

                published_market_count += 1

            if market["status"] == "Suspended":

                suspended_market_count += 1

            for selection in market["selections"]:

                selection_count += 1

                if selection["pending_price"] is not None:

                    pending_count += 1

    if pending_count > 0:

        action_items.append(
            f"Pending price changes: {pending_count}"
        )

    if events_today_count > 0:

        action_items.append(
            f"Events today: {events_today_count}"
        )

    if suspended_market_count > 0:

        action_items.append(
            f"Suspended markets: {suspended_market_count}"
        )

    print()
    print("=" * 50)
    print("      ODDS DISTRIBUTION PLATFORM")
    print("=" * 50)

    print()

    print(f"Events:              {event_count}")
    print(f"Markets:             {market_count}")
    print(f"Selections:          {selection_count}")
    print(f"Clients:             {len(clients)}")

    print()

    print(f"Pending Prices:      {pending_count}")
    print(f"Published Markets:   {published_market_count}")
    print(f"Suspended Markets:   {suspended_market_count}")
    print(f"Events Today:        {events_today_count}")

    print()

    print("ACTION CENTRE")
    print("-------------")

    if action_items:

        for action in action_items:

            print(f"[!] {action}")

    else:

        print("[OK] No actions required.")

    if today_events:

        print("Today's Events")
        print("--------------")

        for time, name in sorted(today_events):

            print(f"{time}  {name}")

    print()

    print("=" * 50)