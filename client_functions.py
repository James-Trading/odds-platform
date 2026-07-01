def create_client(
        name,
        contact,
        email):

    client = {

        "name": name,

        "contact": contact,

        "email": email,

        "status": "Active",

        "feed": {
            "enabled": True,
            "connector": "None",
            "last_price_update": None,
            "last_bet_received": None
        },

        "booked_events": []

    }

    return client

def book_event_for_client(client, event_name):

    if event_name not in client["booked_events"]:

        client["booked_events"].append(event_name)

        print("Event booked.")

    else:

        print("Client already has this event booked.")

def unbook_event_for_client(client, event_name):

    if event_name in client["booked_events"]:

        client["booked_events"].remove(event_name)

        print("Event unbooked.")

    else:

        print("Client does not have this event booked.")