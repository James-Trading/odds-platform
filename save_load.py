import json
import os
from threading import Lock

platform_lock = Lock()

from state.app_state import mark_clean

def save_platform(platform):
    temp_file = "platform.json.tmp"

    with open(temp_file, "w") as file:
        json.dump(
            platform,
            file,
            indent=4
        )
        file.flush()
        os.fsync(file.fileno())

    os.replace(temp_file, "platform.json")

    mark_clean()

def load_platform():

    try:

        with open("platform.json", "r") as file:

            return json.load(file)

    except FileNotFoundError:

        return []