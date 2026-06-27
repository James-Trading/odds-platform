import json


def save_bets(bets):

    with open("bets.json", "w") as file:

        json.dump(
            bets,
            file,
            indent=4
        )


def load_bets():

    try:

        with open("bets.json", "r") as file:

            return json.load(file)

    except FileNotFoundError:

        return []