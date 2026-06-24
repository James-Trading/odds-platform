from datetime import datetime


def add_audit_log(message):

    timestamp = datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )

    with open(
        "audit_log.txt",
        "a"
    ) as file:

        file.write(
            f"{timestamp} - {message}\n"
        )

def display_audit_log():

    print()
    print("AUDIT LOG")
    print("=========")

    try:

        with open("audit_log.txt", "r") as file:

            lines = file.readlines()

            if lines == []:

                print("No audit entries.")

            else:

                for line in lines:

                    print(line.strip())

    except FileNotFoundError:

        print("No audit entries.")