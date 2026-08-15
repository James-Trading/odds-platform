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

CHANGE_LOG_FILE = Path("change_log.json")


def log_event_change(
    event,
    change_type="event_update",
    details=None,
):

    changes = []

    if CHANGE_LOG_FILE.exists():
        try:
            with CHANGE_LOG_FILE.open(
                "r",
                encoding="utf-8",
            ) as file:
                changes = json.load(file)

            if not isinstance(changes, list):
                changes = []

        except (
            json.JSONDecodeError,
            TypeError,
            ValueError,
        ):
            changes = []

    changes.append(
        {
            "change_id": event.get("change_id"),
            "event_id": event.get("id"),
            "event_name": event.get("event_name"),
            "version": event.get("version"),
            "changed_at": event.get("last_updated"),
            "change_type": change_type,
            "details": details or {},
        }
    )

    with CHANGE_LOG_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            changes,
            file,
            indent=4,
        )