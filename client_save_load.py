import json


def save_clients(clients):

    with open("clients.json", "w") as file:

        json.dump(
            clients,
            file,
            indent=4
        )


def load_clients():

    try:

        with open("clients.json", "r") as file:

            return json.load(file)

    except FileNotFoundError:

        return []