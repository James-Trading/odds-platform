from actions.client_actions import (
    handle_add_client,
    handle_view_clients,
    handle_view_client,
    handle_book_event,
    handle_unbook_event,
)


def client_workspace(platform, clients):

    while True:

        print()
        print("=" * 50)
        print("CLIENTS")
        print("=" * 50)
        print()

        print("1 Add Client")
        print("2 View Client")
        print("3 Book Event")
        print("4 Unbook Event")
        print("0 Back")

        choice = input("\nChoice: ")

        if choice == "1":

            handle_add_client(clients)

        elif choice == "2":

            handle_view_client(
                platform,
                clients
            )

        elif choice == "3":

            handle_book_event(
                clients,
                platform
            )

        elif choice == "4":

            handle_unbook_event(clients)

        elif choice == "0":

            break