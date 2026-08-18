import os
import requests


ADMIN_CLIENTS_URL = "https://api.goldliner.co.uk/internal/admin/clients"


def _get_admin_headers():
    admin_key = os.getenv("GTM_ADMIN_API_KEY")

    if not admin_key:
        raise RuntimeError("GTM_ADMIN_API_KEY is not set")

    return {
        "Authorization": f"Bearer {admin_key}"
    }


def save_clients(clients):
    response = requests.post(
        ADMIN_CLIENTS_URL,
        headers=_get_admin_headers(),
        json=clients,
        timeout=10,
    )

    response.raise_for_status()
    return response.json()


def load_clients():
    response = requests.get(
        ADMIN_CLIENTS_URL,
        headers=_get_admin_headers(),
        timeout=10,
    )

    response.raise_for_status()
    return response.json()