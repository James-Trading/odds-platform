from datetime import datetime


def check_event_schedule(platform):

    now = datetime.now()

    print("\nChecking event schedule...")

    for event in platform:

        if "start_time" not in event:

            event["start_time"] = ""
            event["suspend_mode"] = "AUTO"

        if event["start_time"] == "":
            continue

        if event["suspend_mode"] != "AUTO":
            continue

        try:

            start_time = datetime.strptime(
                event["start_time"],
                "%d/%m/%Y %H:%M"
            )

        except ValueError:

            print(f"Invalid start time for {event['event_name']}")

            continue

        if now >= start_time:

            if event["status"] == "Active":

                event["status"] = "Suspended"

                event["displayed"] = False

                print(f"Auto-suspended: {event['event_name']}")