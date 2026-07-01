from client_functions import (
    create_client,
    book_event_for_client,
    unbook_event_for_client
)
from client_save_load import save_clients
from audit_functions import add_audit_log
from display_functions import choose_event

from feeds.client_feeds import display_client_feed


def handle_add_client(clients):

    name = input("Client Name: ")
    contact = input("Contact: ")
    email = input("Email: ")

    client = create_client(
        name,
        contact,
        email
    )

    clients.append(client)

    save_clients(clients)

    add_audit_log(
        f"Client created: {name}"
    )

    print("Client created.")


def handle_view_clients(clients):

    print()
    print("CLIENTS")
    print("=======")

    if clients == []:
        print("No clients.")
        return

    for client in clients:
        print(
            client["name"],
            "-",
            client["status"],
            "-",
            client["email"]
        )

def choose_client(clients):

    print()
    print("CLIENTS")
    print("=======")

    if clients == []:

        print("No clients.")

        return None

    for i, client in enumerate(clients, start=1):

        print(f"{i}. {client['name']}")

    choice = int(input("Client: "))

    return clients[choice - 1]

def handle_book_event(clients, platform):

    client = choose_client(clients)

    if client is None:

        return

    event = choose_event(platform)

    book_event_for_client(
        client,
        event["event_name"]
    )

    save_clients(clients)

    add_audit_log(
        f'{client["name"]} booked {event["event_name"]}'
    )

def handle_view_client(clients):

    client = choose_client(clients)

    if client is None:

        return

    print()

    print("CLIENT DETAILS")
    print("==============")

    print(f"Name: {client['name']}")
    print(f"Contact: {client['contact']}")
    print(f"Email: {client['email']}")
    print(f"Status: {client['status']}")

    print()

    print("Booked Events")
    print("-------------")

    if client["booked_events"] == []:

        print("None")

    else:

        for event in client["booked_events"]:

            print(f"- {event}")
    print()
    print("F Client Feed")
    print("0 Back")

    choice = input("Choice: ").upper()

    if choice == "F":

        display_client_feed(
            clients,
            client
        )

def handle_unbook_event(clients):

    client = choose_client(clients)

    if client is None:

        return

    print()
    print("BOOKED EVENTS")
    print("=============")

    if client["booked_events"] == []:

        print("No booked events.")

        return

    for i, event_name in enumerate(client["booked_events"], start=1):

        print(f"{i}. {event_name}")

    choice = int(input("Event to unbook: "))

    event_name = client["booked_events"][choice - 1]

    unbook_event_for_client(
        client,
        event_name
    )

    save_clients(clients)

    add_audit_log(
        f'{client["name"]} unbooked {event_name}'
    )