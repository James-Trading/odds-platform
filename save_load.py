import json


def save_platform(platform):

    with open("platform.json", "w") as file:

        json.dump(
            platform,
            file,
            indent=4
        )


def load_platform():

    try:

        with open("platform.json", "r") as file:

            return json.load(file)

    except FileNotFoundError:

        return []