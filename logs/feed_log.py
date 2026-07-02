from datetime import datetime


def log_feed_update(client_name, event_name):

    print(
        f"{datetime.now().strftime('%H:%M:%S')} | "
        f"{event_name} | "
        f"{client_name}"
    )