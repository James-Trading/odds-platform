def back_office():

    while True:

        print()
        print("=" * 50)
        print("BACK OFFICE")
        print("=" * 50)
        print()

        print("1 Price History")
        print("2 Audit Log")
        print("3 Reports")
        print("4 Feed History")
        print("5 System Logs")
        print("6 Settings")

        print()
        print("0 Back")

        choice = input("\nChoice: ")

        if choice == "0":
            break