def edit_event_name(event):

    print()
    print(f"Current name: {event['event_name']}")

    new_name = input("New name: ")

    if new_name != "":

        event["event_name"] = new_name

        print("Event name updated.")

def edit_event_start_time(event):

    print()
    print(f"Current start time: {event['start_time']}")

    new_date = input("New Start Date (DD/MM/YYYY): ")
    new_time = input("New Start Time (HH:MM): ")

    if new_date != "" and new_time != "":

        event["start_time"] = new_date + " " + new_time

        print("Start time updated.")


def edit_event_suspend_mode(event):

    print()
    print(f"Current suspend mode: {event['suspend_mode']}")
    print()
    print("1 AUTO")
    print("2 MANUAL")
    print("3 IN_PLAY")

    choice = input("Choice: ")

    if choice == "1":

        event["suspend_mode"] = "AUTO"

    elif choice == "2":

        event["suspend_mode"] = "MANUAL"

    elif choice == "3":

        event["suspend_mode"] = "IN_PLAY"

    print("Suspend mode updated.")


def edit_event_status(event):

    print()
    print(f"Current status: {event['status']}")
    print()
    print("1 Active")
    print("2 Suspended")

    choice = input("Choice: ")

    if choice == "1":

        event["status"] = "Active"
        event["displayed"] = True

    elif choice == "2":

        event["status"] = "Suspended"
        event["displayed"] = False

    print("Event status updated.")