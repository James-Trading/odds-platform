from imports.excel_preview import preview_excel_import

from tkinter import messagebox

from event_functions import create_event, create_market, add_selection

from save_load import save_platform

def import_excel_event(preview, platform):
    event = create_event(
        preview["category"],
        preview["class"],
        preview["type"],
        preview["event"],
    )

    event_date = preview.get("date")
    event_time = preview.get("time")

    if hasattr(event_date, "strftime"):
        event_date = event_date.strftime("%Y-%m-%d")

    if hasattr(event_time, "strftime"):
        event_time = event_time.strftime("%H:%M")

    event["start_time"] = f"{event_date} {event_time}"
    event["status"] = "Draft"
    event["published"] = False
    event["displayed"] = False

    market = create_market(event, preview["market"])

    market["status"] = "Suspended"
    market["published"] = False
    market["displayed"] = False

    for runner in preview["selections"]:
        selection = add_selection(
            market,
            runner["name"],
            str(runner["price"]),
        )

        selection["active"] = False
        selection["displayed"] = False

    platform.append(event)
    save_platform(platform)

    return event