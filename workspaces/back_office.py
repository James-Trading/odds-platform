from audit_functions import display_audit_log

from back_office.system_health import display_system_health

from back_office.reports import (
    display_event_report,
    display_market_report,
)

from back_office.price_history import display_price_history

def reports_menu(platform):

    while True:

        print()
        print("=" * 50)
        print("REPORTS")
        print("=" * 50)
        print()

        print("1 Event Report")
        print("2 Market Report")
        print("0 Back")

        choice = input("\nChoice: ")

        if choice == "1":

            display_event_report(platform)
            input("\nPress Enter...")

        elif choice == "2":

            display_market_report(platform)
            input("\nPress Enter...")

        elif choice == "0":

            break

def back_office(platform, clients):

    while True:

        print()
        print("=" * 50)
        print("BACK OFFICE")
        print("=" * 50)
        print()

        print("1 Audit Log")
        print("2 Reports")
        print("3 Price History")
        print("4 Feed History")
        print("5 System Health")
        print("6 Migrations")
        print("0 Back")

        choice = input("\nChoice: ")

        if choice == "1":

            display_audit_log()

            input("\nPress Enter...")

        elif choice == "2":

            reports_menu(platform)

        elif choice == "3":

            display_price_history(platform)

            input("\nPress Enter...")

        elif choice == "4":

            print("\nFeed History coming soon.")
            input("\nPress Enter...")

        elif choice == "5":

            display_system_health(
                platform,
                clients
            )

            input("\nPress Enter...")

        elif choice == "6":

            print("\nMigrations coming soon.")
            input("\nPress Enter...")

        elif choice == "0":

            break