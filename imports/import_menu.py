from imports.csv_import import (
    preview_event_csv,
    validate_event_csv,
    import_event_markets_from_csv,
)


def import_menu(platform, clients):

    file_path = ""

    while True:

        print()
        print("IMPORT CENTRE")
        print("=============")
        print()

        if file_path == "":
            print("Current file: None")
        else:
            print(f"Current file: {file_path}")

        print()
        print("1 Select CSV")
        print("2 Preview CSV")
        print("3 Validate CSV")
        print("4 Import CSV")
        print("0 Back")

        choice = input("\nChoice: ")

        if choice == "1":

            file_path = input("CSV file: ")

        elif choice == "2":

            if file_path == "":
                print("\nNo CSV selected.")
                input("\nPress Enter...")
                continue

            preview_event_csv(file_path)
            input("\nPress Enter...")

        elif choice == "3":

            if file_path == "":
                print("\nNo CSV selected.")
                input("\nPress Enter...")
                continue

            validate_event_csv(
                file_path,
                platform
            )

            input("\nPress Enter...")

        elif choice == "4":

            if file_path == "":
                print("\nNo CSV selected.")
                input("\nPress Enter...")
                continue

            import_event_markets_from_csv(
                file_path,
                platform,
                clients
            )

            input("\nPress Enter...")

        elif choice == "0":

            break