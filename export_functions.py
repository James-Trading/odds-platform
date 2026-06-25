import json


def export_event(event):

    filename = event["event_name"].replace(" ", "_").lower() + ".json"

    with open(filename, "w") as file:

        json.dump(
            event,
            file,
            indent=4
        )

    print(f"Event exported to {filename}")