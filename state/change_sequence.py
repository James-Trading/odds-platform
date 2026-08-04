import json
from pathlib import Path
from threading import Lock


SEQUENCE_FILE = Path("change_sequence.json")
sequence_lock = Lock()


def next_change_id():
    with sequence_lock:
        current_value = 0

        if SEQUENCE_FILE.exists():
            try:
                with SEQUENCE_FILE.open(
                    "r",
                    encoding="utf-8",
                ) as file:
                    data = json.load(file)

                current_value = int(
                    data.get("last_change_id", 0)
                )

            except (
                json.JSONDecodeError,
                TypeError,
                ValueError,
            ):
                current_value = 0

        next_value = current_value + 1

        with SEQUENCE_FILE.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                {"last_change_id": next_value},
                file,
                indent=4,
            )

        return next_value