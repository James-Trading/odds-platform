import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog

from save_load import save_platform, load_platform
from client_save_load import load_clients, save_clients

from price_engine.price_ladder import (
    PRICE_LADDER,
    set_price,
)

from platform_functions import (
    suspend_platform_selection,
    unsuspend_platform_selection,
    suspend_platform_market,
    unsuspend_platform_market,
)

from audit_functions import add_audit_log

from pricing import probability

from event_functions import (
    create_event,
    create_market,
    add_selection,
    touch_event,
)

from bets.settlement_functions import settle_market_results

from imports.excel_preview import preview_excel_import

from imports.excel_import import import_excel_event

from distribution.feed_functions import (
    get_published_events, 
    get_client_feed,
)

from client_functions import (
    create_client,
    book_event_for_client,
    unbook_event_for_client,
)

from datetime import datetime, timezone, timedelta

from config import API_BASE_URL

import os

import requests

import secrets

ADMIN_PLATFORM_URL = "https://api.goldliner.co.uk/internal/admin/platform"


def load_remote_platform():
    admin_key = os.getenv("GTM_ADMIN_API_KEY")

    if not admin_key:
        raise RuntimeError("GTM_ADMIN_API_KEY is not set")

    response = requests.get(
        ADMIN_PLATFORM_URL,
        headers={
            "Authorization": f"Bearer {admin_key}"
        },
        timeout=10,
    )

    response.raise_for_status()
    return response.json()

ADMIN_PRICE_URL = "https://api.goldliner.co.uk/internal/admin/price"


def save_remote_price(event_id, market_id, selection_id, price_top, price_bottom):
    admin_key = os.getenv("GTM_ADMIN_API_KEY")

    if not admin_key:
        raise RuntimeError("GTM_ADMIN_API_KEY is not set")

    response = requests.post(
        ADMIN_PRICE_URL,
        headers={
            "Authorization": f"Bearer {admin_key}"
        },
        json={
            "event_id": event_id,
            "market_id": market_id,
            "selection_id": selection_id,
            "price_top": price_top,
            "price_bottom": price_bottom,
        },
        timeout=10,
    )

    response.raise_for_status()
    return response.json()

ADMIN_SELECTION_STATE_URL = "https://api.goldliner.co.uk/internal/admin/selection-state"


def save_remote_selection_state(
    event_id,
    market_id,
    selection_id,
    active=None,
    displayed=None,
):
    admin_key = os.getenv("GTM_ADMIN_API_KEY")

    if not admin_key:
        raise RuntimeError("GTM_ADMIN_API_KEY is not set")

    payload = {
        "event_id": event_id,
        "market_id": market_id,
        "selection_id": selection_id,
    }

    if active is not None:
        payload["active"] = active

    if displayed is not None:
        payload["displayed"] = displayed

    response = requests.post(
        ADMIN_SELECTION_STATE_URL,
        headers={
            "Authorization": f"Bearer {admin_key}"
        },
        json=payload,
        timeout=10,
    )

    response.raise_for_status()
    return response.json()

class OddsPlatformGUI:

    def __init__(self, root, platform, clients):

        self.root = root
        self.platform = platform
        self.clients = clients
        self.pending_prices = {}

        self.root.title("Odds Platform")
        self.root.geometry("1200x750")
        self.root.minsize(950, 600)

        self.build_layout()
        self.show_dashboard()
        self.check_scheduled_events()

    def build_layout(self):

        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        # Left navigation
        self.sidebar = ttk.Frame(
            self.main_frame,
            width=210,
            padding=15
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        self.sidebar.pack_propagate(False)

        title = ttk.Label(
            self.sidebar,
            text="ODDS PLATFORM",
            font=("Arial", 16, "bold")
        )

        title.pack(
            pady=(5, 25)
        )

        ttk.Button(
            self.sidebar,
            text="Dashboard",
            command=self.show_dashboard
        ).pack(fill="x", pady=4)

        ttk.Button(
            self.sidebar,
            text="Trading",
            command=self.show_trading
        ).pack(fill="x", pady=4)

        ttk.Button(
            self.sidebar,
            text="Clients",
            command=self.show_clients
        ).pack(fill="x", pady=4)

        ttk.Button(
            self.sidebar,
            text="Event Builder",
            command=self.show_import_centre,
        ).pack(fill="x", pady=4)

        ttk.Button(
            self.sidebar,
            text="Back Office",
            command=self.show_back_office
        ).pack(fill="x", pady=4)

        ttk.Button(
            self.sidebar,
            text="Settings",
            command=lambda: self.show_page("Settings")
        ).pack(fill="x", pady=4)

        # Main content area
        self.content = ttk.Frame(
            self.main_frame,
            padding=25
        )

        self.content.pack(
            side="left",
            fill="both",
            expand=True
        )

    def clear_content(self):

        for widget in self.content.winfo_children():
            widget.destroy()

    def show_dashboard(self):

        self.clear_content()

        # Top row
        top_bar = ttk.Frame(self.content)
        top_bar.pack(fill="x", pady=(0, 20))

        ttk.Label(
            top_bar,
            text="Dashboard",
            font=("Arial", 24, "bold")
        ).pack(side="left")

        self.search_entry = ttk.Entry(
            top_bar,
            font=("Arial", 12),
            width=35
        )

        self.search_entry.pack(
            side="right",
            padx=(10, 0)
        )

        self.search_entry.bind(
            "<Return>",
            lambda event: self.search_dashboard()
        )

        ttk.Button(
            top_bar,
            text="Search",
            command=self.search_dashboard
        ).pack(side="right")

        # Summary cards
        cards = ttk.Frame(self.content)
        cards.pack(fill="x", pady=(0, 25))

        event_count = len(self.platform)

        market_count = sum(
            len(event.get("markets", []))
            for event in self.platform
        )

        selection_count = sum(
            len(market.get("selections", []))
            for event in self.platform
            for market in event.get("markets", [])
        )

        client_count = len(self.clients)

        self.create_summary_card(cards, "Events", str(event_count))
        self.create_summary_card(cards, "Markets", str(market_count))
        self.create_summary_card(cards, "Selections", str(selection_count))
        self.create_summary_card(cards, "Clients", str(client_count))

        # Main dashboard columns
        dashboard_body = ttk.Frame(self.content)
        dashboard_body.pack(fill="both", expand=True)

        left_column = ttk.Frame(dashboard_body)
        left_column.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 10)
        )

        right_column = ttk.Frame(dashboard_body)
        right_column.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(10, 0)
        )

        # Recent events
        recent_frame = ttk.LabelFrame(
            left_column,
            text="Recent Events",
            padding=15
        )

        recent_frame.pack(
            fill="both",
            expand=True,
            pady=(0, 10)
        )

        self.add_event_row(
            recent_frame,
            "Strictly Come Dancing 2026",
            "Active"
        )

        self.add_event_row(
            recent_frame,
            "Love Island 2026",
            "Active"
        )

        self.add_event_row(
            recent_frame,
            "Eurovision 2027",
            "Draft"
        )

        # Favourites
        favourites_frame = ttk.LabelFrame(
            left_column,
            text="Favourite Events",
            padding=15
        )

        favourites_frame.pack(
            fill="both",
            expand=True,
            pady=(10, 0)
        )

        self.add_event_row(
            favourites_frame,
            "General Election",
            "Active"
        )

        self.add_event_row(
            favourites_frame,
            "Celebrity Big Brother",
            "Suspended"
        )

        # Activity panel
        activity_frame = ttk.LabelFrame(
            right_column,
            text="Recent Activity",
            padding=15
        )

        activity_frame.pack(
            fill="both",
            expand=True
        )

        ttk.Label(
            activity_frame,
            text="22:43  Price changed",
            font=("Arial", 11, "bold")
        ).pack(anchor="w")

        ttk.Label(
            activity_frame,
            text="Strictly > Outright > James Dobson\n5/2 → 2/1"
        ).pack(anchor="w", pady=(2, 15))

        ttk.Label(
            activity_frame,
            text="22:38  Market suspended",
            font=("Arial", 11, "bold")
        ).pack(anchor="w")

        ttk.Label(
            activity_frame,
            text="Love Island > Winning Couple"
        ).pack(anchor="w", pady=(2, 15))

        ttk.Label(
            activity_frame,
            text="22:30  Event published",
            font=("Arial", 11, "bold")
        ).pack(anchor="w")

        ttk.Label(
            activity_frame,
            text="Eurovision 2027"
        ).pack(anchor="w")

    def show_clients(self):
        self.clear_content()

        ttk.Label(
            self.content,
            text="Clients",
            font=("Arial", 26, "bold"),
        ).pack(
            anchor="w",
            pady=(0, 15),
        )

        top_bar = ttk.Frame(self.content)
        top_bar.pack(
            fill="x",
            pady=(0, 12),
        )

        ttk.Button(
            top_bar,
            text="Add Client",
            command=self.add_client_popup,
        ).pack(
            side="left",
        )

        ttk.Label(
            top_bar,
            text=f"Total clients: {len(self.clients)}",
        ).pack(
            side="right",
        )

        workspace = ttk.Frame(self.content)
        workspace.pack(
            fill="both",
            expand=True,
        )

        workspace.columnconfigure(
            0,
            weight=1,
        )
        workspace.columnconfigure(
            1,
            weight=2,
        )
        workspace.rowconfigure(
            0,
            weight=1,
        )

        # Left side: client list
        client_list_frame = ttk.LabelFrame(
            workspace,
            text="Client List",
            padding=10,
        )
        client_list_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 10),
        )

        # Right side: selected client details
        self.client_details_frame = ttk.LabelFrame(
            workspace,
            text="Client Details",
            padding=15,
        )
        self.client_details_frame.grid(
            row=0,
            column=1,
            sticky="nsew",
        )

        if not self.clients:
            ttk.Label(
                client_list_frame,
                text="No clients have been added.",
            ).pack(
                anchor="w",
                pady=8,
            )

            ttk.Label(
                self.client_details_frame,
                text="Select or add a client.",
            ).pack(
                anchor="w",
            )
            return

        for client in self.clients:
            client_name = client.get(
                "name",
                "Unnamed Client",
            )

            client_status = client.get(
                "status",
                "Unknown",
            )

            button_text = (
                f"{client_name} — {client_status}"
            )

            ttk.Button(
                client_list_frame,
                text=button_text,
                command=lambda selected_client=client: (
                    self.show_client_details(
                        selected_client
                    )
                ),
            ).pack(
                fill="x",
                pady=3,
            )

        self.show_client_details(
            self.clients[0]
        )

    def show_client_details(self, client):
        for widget in self.client_details_frame.winfo_children():
            widget.destroy()

        client_name = client.get(
            "name",
            "Unnamed Client",
        )

        contact = client.get(
            "contact",
            "Not set",
        )

        email = client.get(
            "email",
            "Not set",
        )

        status = client.get(
            "status",
            "Unknown",
        )

        feed = client.get(
            "feed",
            {},
        )

        feed_enabled = (
            "Enabled"
            if feed.get("enabled", False)
            else "Disabled"
        )

        api_key = feed.get(
            "api_key",
            "Not generated",
        )

        booked_events = client.get(
            "booked_events",
            [],
        )

        ttk.Label(
            self.client_details_frame,
            text=client_name,
            font=("Arial", 20, "bold"),
        ).pack(
            anchor="w",
            pady=(0, 15),
        )

        details_grid = ttk.Frame(
            self.client_details_frame
        )
        details_grid.pack(
            fill="x",
        )

        # Get live WebSocket connection status
        connection_status = "Disconnected"
        connected_since = "-"
        last_update = "-"

        try:
            response = requests.get(
                f"{API_BASE_URL}/internal/connections",
                timeout=1
            )

            if response.status_code == 200:
                connection_data = response.json()
                client_name = client.get("name", "")
                live_client = connection_data.get("clients", {}).get(
                    client_name,
                    {}
                )

                if live_client.get("connected"):
                    connection_status = "Connected"

                connected_since_raw = live_client.get("connected_at")
                last_update_raw = live_client.get("last_update_sent")

                if connected_since_raw:
                    connected_since = (
                        datetime.fromisoformat(connected_since_raw)
                        .astimezone()
                        .strftime("%d/%m/%Y %H:%M")
                    )

                if last_update_raw:
                    last_update = (
                        datetime.fromisoformat(last_update_raw)
                        .astimezone()
                        .strftime("%d/%m/%Y %H:%M")
                    )

        except requests.RequestException:
            connection_status = "API Offline"


        detail_rows = [
            ("Contact", contact),
            ("Email", email),
            ("Status", status),
            ("Feed", feed_enabled),
            ("Live connection", connection_status),
            ("Connected since", connected_since),
            ("Last update", last_update),
            ("API key", api_key),
        ]

        for row_number, (label, value) in enumerate(
            detail_rows
        ):
            ttk.Label(
                details_grid,
                text=f"{label}:",
                font=("Arial", 10, "bold"),
            ).grid(
                row=row_number,
                column=0,
                sticky="nw",
                padx=(0, 15),
                pady=5,
            )

            ttk.Label(
                details_grid,
                text=value,
                wraplength=500,
            ).grid(
                row=row_number,
                column=1,
                sticky="nw",
                pady=5,
            )

        button_frame = ttk.Frame(
            self.client_details_frame
        )

        button_frame.pack(
            fill="x",
            pady=(15, 0),
        )

        ttk.Button(
            button_frame,
            text="Edit Client",
            command=lambda: self.edit_client_popup(
                client
            ),
        ).pack(
            side="left",
        )

        ttk.Button(
            button_frame,
            text="Book Events",
            command=lambda: self.manage_client_events_popup(
                client
            ),
        ).pack(
            side="left",
            padx=(8, 0),
        )

        ttk.Button(
            button_frame,
            text="Copy API Key",
            command=lambda: self.copy_client_api_key(
                client
            ),
        ).pack(
            side="left",
            padx=(8, 0),
        )

        ttk.Button(
            button_frame,
            text="Regenerate API Key",
            command=lambda: self.regenerate_client_api_key(
                client
            ),
        ).pack(
            side="left",
            padx=(8, 0),
        )

        feed_button_text = (
            "Disable Feed"
            if feed.get("enabled", False)
            else "Enable Feed"
        )

        ttk.Button(
            button_frame,
            text=feed_button_text,
            command=lambda: self.toggle_client_feed(
                client
            ),
        ).pack(
            side="left",
            padx=(8, 0),
        )

        ttk.Separator(
            self.client_details_frame,
            orient="horizontal",
        ).pack(
            fill="x",
            pady=15,
        )

        ttk.Label(
            self.client_details_frame,
            text="Booked Events",
            font=("Arial", 13, "bold"),
        ).pack(
            anchor="w",
            pady=(0, 8),
        )

        if booked_events:
            for event_name in booked_events:
                ttk.Label(
                    self.client_details_frame,
                    text=f"• {event_name}",
                ).pack(
                    anchor="w",
                    pady=2,
                )
        else:
            ttk.Label(
                self.client_details_frame,
                text="No events currently booked.",
            ).pack(
                anchor="w",
            )

    def add_client_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Add Client")
        popup.geometry("450x280")
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.grab_set()

        form = ttk.Frame(
            popup,
            padding=20,
        )
        form.pack(
            fill="both",
            expand=True,
        )

        name_var = tk.StringVar()
        contact_var = tk.StringVar()
        email_var = tk.StringVar()

        fields = [
            ("Client name", name_var),
            ("Contact name", contact_var),
            ("Email", email_var),
        ]

        for row_number, (label, variable) in enumerate(
            fields
        ):
            ttk.Label(
                form,
                text=label,
            ).grid(
                row=row_number,
                column=0,
                sticky="w",
                pady=8,
            )

            ttk.Entry(
                form,
                textvariable=variable,
                width=35,
            ).grid(
                row=row_number,
                column=1,
                sticky="ew",
                padx=(15, 0),
                pady=8,
            )

        def save_new_client():
            name = name_var.get().strip()
            contact = contact_var.get().strip()
            email = email_var.get().strip()

            if not name:
                messagebox.showwarning(
                    "Add Client",
                    "Client name cannot be blank.",
                    parent=popup,
                )
                return

            new_client = create_client(
                name,
                contact,
                email,
            )

            self.clients.append(
                new_client
            )

            save_clients(
                self.clients
            )

            popup.destroy()
            self.show_clients()

        button_frame = ttk.Frame(form)
        button_frame.grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="e",
            pady=(20, 0),
        )

        ttk.Button(
            button_frame,
            text="Cancel",
            command=popup.destroy,
        ).pack(
            side="right",
            padx=(8, 0),
        )

        ttk.Button(
            button_frame,
            text="Add Client",
            command=save_new_client,
        ).pack(
            side="right",
        )

        form.columnconfigure(
            1,
            weight=1,
        )

    def copy_client_api_key(self, client):
        api_key = client.get(
            "feed",
            {},
        ).get(
            "api_key",
            "",
        )

        if not api_key:
            messagebox.showwarning(
                "API Key",
                "This client does not have an API key.",
            )
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(api_key)
        self.root.update()

        messagebox.showinfo(
            "API Key",
            "API key copied to clipboard.",
        )

    def toggle_client_feed(self, client):
        feed = client.setdefault(
            "feed",
            {},
        )

        feed["enabled"] = not feed.get(
            "enabled",
            False,
        )

        save_clients(
            self.clients
        )

        self.show_client_details(
            client
        )

    def regenerate_client_api_key(self, client):
        if not messagebox.askyesno(
            "Regenerate API Key",
            (
                "Regenerate this client's API key?\n\n"
                "The existing key will stop working immediately."
            ),
            parent=self.root,
        ):
            return

        feed = client.setdefault("feed", {})

        new_api_key = f"GTM_{secrets.token_hex(16)}"
        feed["api_key"] = new_api_key

        save_clients(self.clients)

        self.show_client_details(client)

        messagebox.showinfo(
            "API Key Regenerated",
            "A new API key has been generated.",
            parent=self.root,
        )

    def edit_client_popup(self, client):
        popup = tk.Toplevel(self.root)
        popup.title("Edit Client")
        popup.geometry("450x330")
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.grab_set()

        form = ttk.Frame(
            popup,
            padding=20,
        )

        form.pack(
            fill="both",
            expand=True,
        )

        name_var = tk.StringVar(
            value=client.get("name", "")
        )

        contact_var = tk.StringVar(
            value=client.get("contact", "")
        )

        email_var = tk.StringVar(
            value=client.get("email", "")
        )

        status_var = tk.StringVar(
            value=client.get("status", "Active")
        )

        fields = [
            ("Client name", name_var),
            ("Contact name", contact_var),
            ("Email", email_var),
        ]

        for row_number, (label, variable) in enumerate(
            fields
        ):
            ttk.Label(
                form,
                text=label,
            ).grid(
                row=row_number,
                column=0,
                sticky="w",
                pady=8,
            )

            ttk.Entry(
                form,
                textvariable=variable,
                width=35,
            ).grid(
                row=row_number,
                column=1,
                sticky="ew",
                padx=(15, 0),
                pady=8,
            )

        ttk.Label(
            form,
            text="Status",
        ).grid(
            row=3,
            column=0,
            sticky="w",
            pady=8,
        )

        ttk.Combobox(
            form,
            textvariable=status_var,
            values=[
                "Active",
                "Inactive",
            ],
            state="readonly",
            width=32,
        ).grid(
            row=3,
            column=1,
            sticky="ew",
            padx=(15, 0),
            pady=8,
        )

        def save_client_changes():
            name = name_var.get().strip()

            if not name:
                messagebox.showwarning(
                    "Edit Client",
                    "Client name cannot be blank.",
                    parent=popup,
                )
                return

            client["name"] = name
            client["contact"] = (
                contact_var.get().strip()
            )
            client["email"] = (
                email_var.get().strip()
            )
            client["status"] = status_var.get()

            save_clients(
                self.clients
            )

            popup.destroy()
            self.show_clients()

        button_frame = ttk.Frame(form)

        button_frame.grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="e",
            pady=(20, 0),
        )

        ttk.Button(
            button_frame,
            text="Cancel",
            command=popup.destroy,
        ).pack(
            side="right",
            padx=(8, 0),
        )

        ttk.Button(
            button_frame,
            text="Save",
            command=save_client_changes,
        ).pack(
            side="right",
        )

        form.columnconfigure(
            1,
            weight=1,
        )

    def manage_client_events_popup(self, client):
        popup = tk.Toplevel(self.root)
        popup.title(
            f"Manage Events - {client.get('name', 'Client')}"
        )
        popup.geometry("520x480")
        popup.transient(self.root)
        popup.grab_set()

        main_frame = ttk.Frame(
            popup,
            padding=15,
        )

        main_frame.pack(
            fill="both",
            expand=True,
        )

        ttk.Label(
            main_frame,
            text="Select the events this client should receive:",
            font=("Arial", 11, "bold"),
        ).pack(
            anchor="w",
            pady=(0, 12),
        )

        booked_events = client.setdefault(
            "booked_events",
            [],
        )

        event_variables = {}

        events_frame = ttk.Frame(
            main_frame
        )

        events_frame.pack(
            fill="both",
            expand=True,
        )

        for event in self.platform:
            event_name = event.get(
                "event_name",
                "Unnamed Event",
            )

            variable = tk.BooleanVar(
                value=event_name in booked_events
            )

            event_variables[event_name] = variable

            event_row = ttk.Frame(events_frame)
            event_row.pack(
                fill="x",
                pady=3,
            )

            ttk.Checkbutton(
                event_row,
                text=event_name,
                variable=variable,
            ).pack(
                side="left",
                anchor="w",
            )

            ttk.Button(
                event_row,
                text="Markets...",
                command=lambda selected_event=event: (
                    self.manage_client_market_access_popup(
                        client,
                        selected_event,
                    )
                ),
            ).pack(
                side="right",
            )

        def save_event_bookings():
            for event_name, variable in (
                event_variables.items()
            ):
                is_booked = (
                    event_name
                    in client["booked_events"]
                )

                if variable.get() and not is_booked:
                    book_event_for_client(
                        client,
                        event_name,
                    )

                elif not variable.get() and is_booked:
                    unbook_event_for_client(
                        client,
                        event_name,
                    )

            save_clients(
                self.clients
            )

            popup.destroy()
            self.show_client_details(
                client
            )

        button_frame = ttk.Frame(
            main_frame
        )

        button_frame.pack(
            fill="x",
            pady=(15, 0),
        )

        ttk.Button(
            button_frame,
            text="Cancel",
            command=popup.destroy,
        ).pack(
            side="right",
            padx=(8, 0),
        )

        ttk.Button(
            button_frame,
            text="Save Bookings",
            command=save_event_bookings,
        ).pack(
            side="right",
        )

    def manage_client_market_access_popup(self, client, event):
        event_name = event.get(
            "event_name",
            "Unnamed Event",
        )

        event_id = event.get("id")

        popup = tk.Toplevel(self.root)
        popup.title(
            f"Market Access - {event_name}"
        )
        popup.geometry("480x500")
        popup.transient(self.root)
        popup.grab_set()

        main_frame = ttk.Frame(
            popup,
            padding=15,
        )
        main_frame.pack(
            fill="both",
            expand=True,
        )

        ttk.Label(
            main_frame,
            text=f"Market Access - {event_name}",
            font=("Arial", 14, "bold"),
        ).pack(
            anchor="w",
            pady=(0, 10),
        )

        ttk.Label(
            main_frame,
            text=(
                "Select the markets this client should receive."
            ),
        ).pack(
            anchor="w",
            pady=(0, 12),
        )

        market_access = client.setdefault(
            "market_access",
            {},
        )

        # Prefer UUID-based access.
        # Fall back to old name-based access for existing clients.
        existing_access = market_access.get(event_id)

        if existing_access is None:
            existing_access = market_access.get(event_name)

        market_variables = {}

        markets_frame = ttk.Frame(main_frame)
        markets_frame.pack(
            fill="both",
            expand=True,
        )

        for market in event.get("markets", []):
            market_name = market.get(
                "name",
                "Unnamed Market",
            )

            market_id = market.get("id")

            # No restriction = every market selected.
            if existing_access is None:
                selected = True
            else:
                # UUID is the new system.
                # Name check keeps old saved permissions working.
                selected = (
                    market_id in existing_access
                    or market_name in existing_access
                )

            variable = tk.BooleanVar(
                value=selected
            )

            market_variables[market_id] = variable

            ttk.Checkbutton(
                markets_frame,
                text=market_name,
                variable=variable,
            ).pack(
                anchor="w",
                pady=4,
            )

        def save_market_access():
            selected_market_ids = [
                market_id
                for market_id, variable
                in market_variables.items()
                if variable.get()
            ]

            all_market_ids = list(
                market_variables.keys()
            )

            # Remove any old name-based record.
            market_access.pop(
                event_name,
                None,
            )

            if set(selected_market_ids) == set(all_market_ids):
                # All markets selected = unrestricted.
                market_access.pop(
                    event_id,
                    None,
                )
            else:
                market_access[event_id] = (
                    selected_market_ids
                )

            save_clients(self.clients)

            messagebox.showinfo(
                "Market Access",
                "Market access saved.",
                parent=popup,
            )

            popup.destroy()

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(
            fill="x",
            pady=(15, 0),
        )

        ttk.Button(
            button_frame,
            text="Save",
            command=save_market_access,
        ).pack(
            side="left",
        )

        ttk.Button(
            button_frame,
            text="Cancel",
            command=popup.destroy,
        ).pack(
            side="right",
        )

    def show_trading(self, filtered_events=None):

        self.clear_content()

        self.archive_old_events()

        top_bar = ttk.Frame(self.content)
        top_bar.pack(fill="x", pady=(0, 20))

        ttk.Label(
            top_bar,
            text="Trading",
            font=("Arial", 24, "bold")
        ).pack(side="left")

        self.trading_search_entry = ttk.Entry(
            top_bar,
            width=35,
            font=("Arial", 12)
        )

        self.trading_search_entry.pack(
            side="right",
            padx=(10, 0),
        )

        self.trading_search_entry.bind(
            "<Return>",
            lambda event: self.filter_trading_events(),
        )

        events_frame = ttk.LabelFrame(
            self.content,
            text="Events",
            padding=15
        )

        events_frame.pack(
            fill="both",
            expand=True
        )

        events_to_show = (
            filtered_events
            if filtered_events is not None
            else self.platform
        )

        events_to_show = [
            event
            for event in events_to_show
            if not event.get("archived", False)
        ]

        for event in events_to_show:

            event_name = event.get(
                "event_name",
                "Unnamed Event"
            )

            status = (
                "Active"
                if event.get("active", True)
                else "Suspended"
            )

            row = ttk.Frame(events_frame)
            row.pack(fill="x", pady=5)

            ttk.Button(
                row,
                text=event_name,
                command=lambda selected_event=event:
                    self.show_event_screen(selected_event)
            ).pack(
                side="left",
                fill="x",
                expand=True
            )

            ttk.Label(
                row,
                text=status,
                width=12,
                anchor="center"
            ).pack(
                side="right",
                padx=(10, 0)
            )

    def filter_trading_events(self):
        search_term = (
            self.trading_search_entry.get()
            .strip()
            .lower()
        )

        if not search_term:
            self.show_trading()
            return

        matching_events = [
            event
            for event in self.platform
            if search_term
            in event.get(
                "event_name",
                "",
            ).lower()
        ]

        self.show_trading(
            filtered_events=matching_events
        )

    def show_event_screen(self, event):

        self.clear_content()

        ttk.Button(
            self.content,
            text="← Back to Trading",
            command=self.show_trading
        ).pack(anchor="w", pady=(0, 15))

        ttk.Label(
            self.content,
            text=event.get("event_name", "Unnamed Event"),
            font=("Arial", 24, "bold")
        ).pack(anchor="w")

        status = "Published" if event.get("published") else "Draft"

        ttk.Label(
            self.content,
            text=f"Status: {status}",
            font=("Arial", 11)
        ).pack(anchor="w", pady=(0, 15))

        button_text = (
            "Unpublish Event"
            if event.get("published")
            else "Publish Event"
        )

        ttk.Button(
            self.content,
            text=button_text,
            command=lambda: self.toggle_event_publish(event)
        ).pack(anchor="w", pady=(0, 20))

        ttk.Label(
            self.content,
            text="Markets",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", pady=(25, 10))

        ttk.Button(
            self.content,
            text="+ Add Market",
            command=lambda: self.create_market_popup(event),
        ).pack(
            anchor="w",
            pady=(0, 10),
        )

        for market in event.get("markets", []):

            ttk.Button(
                self.content,
                text=market.get("name", "Unnamed Market"),
                command=lambda selected_market=market:
                    self.show_market_screen(
                        event,
                        selected_market
                    )
            ).pack(
                fill="x",
                anchor="w",
                pady=4
            )

        ttk.Button(
            self.content,
            text="Manage Markets",
            command=lambda: self.manage_markets_popup(event),
        ).pack(
            anchor="w",
            pady=(0, 10),
        )

    def manage_markets_popup(self, event):
        popup = tk.Toplevel(self.root)
        popup.title("Manage Markets")
        popup.geometry("600x450")
        popup.transient(self.root)
        popup.grab_set()

        main_frame = ttk.Frame(
            popup,
            padding=15,
        )
        main_frame.pack(
            fill="both",
            expand=True,
        )

        ttk.Label(
            main_frame,
            text=f"Manage Markets - {event.get('event_name', 'Event')}",
            font=("Arial", 15, "bold"),
        ).pack(
            anchor="w",
            pady=(0, 15),
        )

        market_list = tk.Listbox(
            main_frame,
            height=14,
        )
        market_list.pack(
            fill="both",
            expand=True,
            pady=(0, 15),
        )

        def refresh_market_list():
            market_list.delete(0, "end")

            for market in event.get("markets", []):
                market_list.insert(
                    "end",
                    market.get("name", "Unnamed Market"),
                )

        def get_selected_market():
            selection = market_list.curselection()

            if not selection:
                messagebox.showwarning(
                    "Manage Markets",
                    "Please select a market first.",
                    parent=popup,
                )
                return None

            index = selection[0]

            return event.get(
                "markets",
                [],
            )[index]

        def rename_market():
            market = get_selected_market()

            if market is None:
                return

            new_name = simpledialog.askstring(
                "Rename Market",
                "Enter new market name:",
                initialvalue=market.get("name", ""),
                parent=popup,
            )

            if new_name is None:
                return

            new_name = new_name.strip()

            if not new_name:
                messagebox.showwarning(
                    "Rename Market",
                    "Market name cannot be blank.",
                    parent=popup,
                )
                return

            market["name"] = new_name

            touch_event(event)
            save_platform(self.platform)

            refresh_market_list()

        def delete_market():
            market = get_selected_market()

            if market is None:
                return

            market_name = market.get(
                "name",
                "Unnamed Market",
            )

            confirmed = messagebox.askyesno(
                "Delete Market",
                f"Delete '{market_name}'?\n\n"
                "This will also delete all selections in this market.",
                parent=popup,
            )

            if not confirmed:
                return

            event["markets"].remove(market)

            touch_event(event)
            save_platform(self.platform)

            refresh_market_list()

        button_frame = ttk.Frame(
            main_frame
        )
        button_frame.pack(
            fill="x",
        )

        ttk.Button(
            button_frame,
            text="Rename Market",
            command=rename_market,
        ).pack(
            side="left",
        )

        ttk.Button(
            button_frame,
            text="Delete Market",
            command=delete_market,
        ).pack(
            side="left",
            padx=(8, 0),
        )

        ttk.Button(
            button_frame,
            text="Close",
            command=lambda: (
                popup.destroy(),
                self.show_event_screen(event),
            ),
        ).pack(
            side="right",
        )

        refresh_market_list()

    def toggle_event_publish(self, event):

        event["published"] = not event.get("published", False)

        save_platform(self.platform)

        self.show_event_screen(event)

    def toggle_event_publish_from_market(
        self,
        event,
        market,
    ):
        event["published"] = not event.get(
            "published",
            False,
        )

        touch_event(event)
        save_platform(self.platform)

        self.show_market_screen(
            event,
            market,
        )

    def show_back_office(self):
        self.clear_content()

        ttk.Label(
            self.content,
            text="Back Office",
            font=("Arial", 22, "bold")
        ).pack(anchor="w", pady=(0, 20))

        # ----- Summary -----
        summary_frame = ttk.LabelFrame(
            self.content,
            text="System Overview",
            padding=15
        )
        summary_frame.pack(fill="x", pady=(0, 15))

        clients = getattr(self, "clients", [])

        enabled_clients = sum(
            1
            for client in clients
            if client.get("feed", {}).get("enabled", False)
        )

        published_events = sum(
            1
            for event in self.platform
            if event.get("published", False)
        )

        ttk.Label(
            summary_frame,
            text=f"Clients Enabled: {enabled_clients} / {len(clients)}"
        ).grid(row=0, column=0, sticky="w", padx=(0, 40))

        ttk.Label(
            summary_frame,
            text=f"Published Events: {published_events}"
        ).grid(row=0, column=1, sticky="w")

        # ----- Recent feed activity -----
        activity_frame = ttk.LabelFrame(
            self.content,
            text="Recent Feed Activity",
            padding=15
        )
        activity_frame.pack(fill="both", expand=True)

        activity_text = tk.Text(
            activity_frame,
            height=14,
            wrap="word"
        )
        activity_text.pack(fill="both", expand=True)

        try:
            with open(
                "logs/activity_log.txt",
                "r",
                encoding="utf-8"
            ) as file:
                lines = file.readlines()

            recent_lines = lines[-20:]

            if recent_lines:
                activity_text.insert(
                    "1.0",
                    "".join(recent_lines)
                )
            else:
                activity_text.insert(
                    "1.0",
                    "No feed activity recorded yet."
                )

        except FileNotFoundError:
            activity_text.insert(
                "1.0",
                "No activity log found."
            )

        activity_text.config(state="disabled")

        # ----- Tools -----
        tools_frame = ttk.Frame(self.content)
        tools_frame.pack(fill="x", pady=(15, 0))

        ttk.Button(
            tools_frame,
            text="Refresh",
            command=self.show_back_office
        ).pack(side="left")

        ttk.Button(
            tools_frame,
            text="Audit Log",
            command=self.show_audit_log
        ).pack(side="left", padx=5)

        ttk.Button(
            tools_frame,
            text="System Health",
            command=self.show_system_health
        ).pack(side="left", padx=5)

        ttk.Button(
            tools_frame,
            text="Feed History",
            command=self.show_feed_history
        ).pack(side="left", padx=5)

        ttk.Button(
            self.content,
            text="Archived Events",
            command=self.show_archived_events,
        ).pack(
            anchor="w",
            pady=5,
        )

    def show_audit_log(self):
        self.clear_content()

        ttk.Label(
            self.content,
            text="Audit Log",
            font=("Arial", 22, "bold"),
        ).pack(
            anchor="w",
            pady=(0, 15),
        )

        top_bar = ttk.Frame(
            self.content
        )
        top_bar.pack(
            fill="x",
            pady=(0, 10),
        )

        ttk.Button(
            top_bar,
            text="← Back to Back Office",
            command=self.show_back_office,
        ).pack(
            side="left",
        )

        ttk.Button(
            top_bar,
            text="Refresh",
            command=self.show_audit_log,
        ).pack(
            side="left",
            padx=(8, 0),
        )

        log_frame = ttk.LabelFrame(
            self.content,
            text="Recorded Activity",
            padding=10,
        )

        log_frame.pack(
            fill="both",
            expand=True,
        )

        audit_text = tk.Text(
            log_frame,
            wrap="word",
            state="normal",
        )

        audit_text.pack(
            fill="both",
            expand=True,
        )

        try:
            with open(
                "audit_log.txt",
                "r",
                encoding="utf-8",
            ) as file:
                lines = file.readlines()

            if lines:
                audit_text.insert(
                    "1.0",
                    "".join(reversed(lines)),
                )
            else:
                audit_text.insert(
                    "1.0",
                    "No audit activity recorded yet.",
                )

        except FileNotFoundError:
            audit_text.insert(
                "1.0",
                "No audit log file found.",
            )

        audit_text.config(
            state="disabled"
        )

    def show_system_health(self):
        self.clear_content()

        ttk.Label(
            self.content,
            text="System Health",
            font=("Arial", 22, "bold"),
        ).pack(anchor="w", pady=(0, 15))

        top_bar = ttk.Frame(self.content)
        top_bar.pack(fill="x", pady=(0, 15))

        ttk.Button(
            top_bar,
            text="← Back to Back Office",
            command=self.show_back_office,
        ).pack(side="left")

        ttk.Button(
            top_bar,
            text="Refresh",
            command=self.show_system_health,
        ).pack(side="left", padx=(8, 0))

        # -------------------------
        # Calculate platform totals
        # -------------------------

        events = len(self.platform)

        markets = sum(
            len(event.get("markets", []))
            for event in self.platform
        )

        selections = sum(
            len(market.get("selections", []))
            for event in self.platform
            for market in event.get("markets", [])
        )

        clients = getattr(self, "clients", [])

        suspended_events = sum(
            1
            for event in self.platform
            if not event.get("active", True)
        )

        suspended_markets = sum(
            1
            for event in self.platform
            for market in event.get("markets", [])
            if str(
                market.get("status", "ACTIVE")
            ).upper() == "SUSPENDED"
        )

        published_events = sum(
            1
            for event in self.platform
            if event.get("published", False)
        )

        unpublished_events = len(self.platform) - published_events


        try:
            with open(
                "audit_log.txt",
                "r",
                encoding="utf-8",
            ) as file:
                audit_entries = len(file.readlines())
        except FileNotFoundError:
            audit_entries = 0

        # -------------------------
        # Platform section
        # -------------------------

        platform_frame = ttk.LabelFrame(
            self.content,
            text="Platform",
            padding=15,
        )
        platform_frame.pack(fill="x", pady=(0, 15))

        platform_stats = [
            ("Events", events),
            ("Markets", markets),
            ("Selections", selections),
            ("Clients", len(clients)),
        ]

        for row, (label, value) in enumerate(platform_stats):
            ttk.Label(
                platform_frame,
                text=label,
            ).grid(
                row=row,
                column=0,
                sticky="w",
                padx=(0, 40),
                pady=4,
            )

            ttk.Label(
                platform_frame,
                text=str(value),
                font=("Arial", 11, "bold"),
            ).grid(
                row=row,
                column=1,
                sticky="w",
                pady=4,
            )

        # -------------------------
        # Trading status
        # -------------------------

        trading_frame = ttk.LabelFrame(
            self.content,
            text="Trading Status",
            padding=15,
        )
        trading_frame.pack(fill="x", pady=(0, 15))

        trading_stats = [
            ("Suspended Events", suspended_events),
            ("Suspended Markets", suspended_markets),
            ("Published Events", published_events),
            ("Unpublished Events", unpublished_events),
        ]

        for row, (label, value) in enumerate(trading_stats):
            ttk.Label(
                trading_frame,
                text=label,
            ).grid(
                row=row,
                column=0,
                sticky="w",
                padx=(0, 40),
                pady=4,
            )

            ttk.Label(
                trading_frame,
                text=str(value),
                font=("Arial", 11, "bold"),
            ).grid(
                row=row,
                column=1,
                sticky="w",
                pady=4,
            )

        # -------------------------
        # Logs
        # -------------------------

        logs_frame = ttk.LabelFrame(
            self.content,
            text="Logs",
            padding=15,
        )
        logs_frame.pack(fill="x")

        ttk.Label(
            logs_frame,
            text="Audit Entries",
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, 40),
            pady=4,
        )

        ttk.Label(
            logs_frame,
            text=str(audit_entries),
            font=("Arial", 11, "bold"),
        ).grid(
            row=0,
            column=1,
            sticky="w",
            pady=4,
        )

    def show_archived_events(self):
        self.clear_content()

        ttk.Button(
            self.content,
            text="← Back to Back Office",
            command=self.show_back_office,
        ).pack(
            anchor="w",
            pady=(0, 15),
        )

        ttk.Label(
            self.content,
            text="Archived Events",
            font=("Arial", 24, "bold"),
        ).pack(
            anchor="w",
            pady=(0, 15),
        )

        archived_events = [
            event
            for event in self.platform
            if event.get("archived", False)
        ]

        if not archived_events:
            ttk.Label(
                self.content,
                text="No archived events.",
            ).pack(
                anchor="w",
                pady=10,
            )
            return

        table_frame = ttk.Frame(self.content)
        table_frame.pack(
            fill="both",
            expand=True,
        )

        columns = (
            "event",
            "category",
            "start_time",
            "status",
        )

        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=15,
        )

        tree.heading(
            "event",
            text="Event",
        )
        tree.heading(
            "category",
            text="Category",
        )
        tree.heading(
            "start_time",
            text="Start Time",
        )
        tree.heading(
            "status",
            text="Status",
        )

        tree.column(
            "event",
            width=300,
        )
        tree.column(
            "category",
            width=150,
        )
        tree.column(
            "start_time",
            width=160,
        )
        tree.column(
            "status",
            width=120,
        )

        tree.pack(
            fill="both",
            expand=True,
        )

        for index, event in enumerate(archived_events):
            tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    event.get(
                        "event_name",
                        "Unnamed Event",
                    ),
                    event.get(
                        "category",
                        "",
                    ),
                    event.get(
                        "start_time",
                        "",
                    ),
                    event.get(
                        "status",
                        "",
                    ),
                ),
            )

        def get_selected_event():
            selected = tree.selection()

            if not selected:
                messagebox.showwarning(
                    "Archived Events",
                    "Please select an event first.",
                )
                return None

            index = int(selected[0])

            return archived_events[index]

        def open_event():
            event = get_selected_event()

            if event is None:
                return

            self.show_event_screen(event)

        def restore_event():
            event = get_selected_event()

            if event is None:
                return

            event_name = event.get(
                "event_name",
                "Unnamed Event",
            )

            confirmed = messagebox.askyesno(
                "Restore Event",
                f"Restore '{event_name}' to Trading?",
            )

            if not confirmed:
                return

            event["archived"] = False

            touch_event(event)
            save_platform(self.platform)

            self.show_archived_events()

        button_frame = ttk.Frame(
            self.content
        )
        button_frame.pack(
            fill="x",
            pady=(10, 0),
        )

        ttk.Button(
            button_frame,
            text="Open Event",
            command=open_event,
        ).pack(
            side="left",
        )

        ttk.Button(
            button_frame,
            text="Restore Event",
            command=restore_event,
        ).pack(
            side="left",
            padx=(10, 0),
        )

    def show_feed_history(self):
        self.clear_content()

        ttk.Label(
            self.content,
            text="Feed History",
            font=("Arial", 22, "bold"),
        ).pack(anchor="w", pady=(0, 15))

        top_bar = ttk.Frame(self.content)
        top_bar.pack(fill="x", pady=(0, 10))

        ttk.Button(
            top_bar,
            text="← Back to Back Office",
            command=self.show_back_office,
        ).pack(side="left")

        # -------------------------
        # Client filter
        # -------------------------
        ttk.Label(
            top_bar,
            text="Client:",
        ).pack(
            side="left",
            padx=(20, 6),
        )

        client_names = [
            client.get("name", "Unnamed Client")
            for client in self.clients
        ]

        filter_options = [
            "All Clients",
            *client_names,
        ]

        client_filter_var = tk.StringVar(
            value="All Clients"
        )

        client_filter = ttk.Combobox(
            top_bar,
            textvariable=client_filter_var,
            values=filter_options,
            state="readonly",
            width=25,
        )

        client_filter.pack(
            side="left"
        )

        feed_frame = ttk.LabelFrame(
            self.content,
            text="Client Feed Activity",
            padding=10,
        )

        feed_frame.pack(
            fill="both",
            expand=True,
        )

        feed_text = tk.Text(
            feed_frame,
            wrap="word",
        )

        feed_text.pack(
            fill="both",
            expand=True,
        )

        def load_feed_history():
            feed_text.config(state="normal")
            feed_text.delete("1.0", "end")

            selected_client = (
                client_filter_var.get()
            )

            try:
                with open(
                    "logs/activity_log.txt",
                    "r",
                    encoding="utf-8",
                ) as file:
                    lines = file.readlines()

                feed_lines = [
                    line
                    for line in lines
                    if (
                        "feed" in line.lower()
                        or "websocket" in line.lower()
                        or "received" in line.lower()
                        or "requested" in line.lower()
                        or "connected" in line.lower()
                    )
                ]

                if selected_client != "All Clients":
                    feed_lines = [
                        line
                        for line in feed_lines
                        if selected_client.lower()
                        in line.lower()
                    ]

                if feed_lines:
                    feed_text.insert(
                        "1.0",
                        "".join(
                            reversed(
                                feed_lines[-100:]
                            )
                        ),
                    )
                else:
                    feed_text.insert(
                        "1.0",
                        "No matching feed activity found.",
                    )

            except FileNotFoundError:
                feed_text.insert(
                    "1.0",
                    "No activity log found.",
                )

            feed_text.config(
                state="disabled"
            )

        ttk.Button(
            top_bar,
            text="Refresh",
            command=load_feed_history,
        ).pack(
            side="left",
            padx=(8, 0),
        )

        client_filter.bind(
            "<<ComboboxSelected>>",
            lambda event: load_feed_history(),
        )

        load_feed_history()

    def show_market_screen(self, event, market):
        self.clear_content()

        # Back button
        ttk.Button(
            self.content,
            text="← Back to Event",
            command=lambda: self.show_event_screen(event),
        ).pack(anchor="w", pady=(0, 15))

        # Market heading
        ttk.Label(
            self.content,
            text=market.get("name", "Unnamed Market"),
            font=("Arial", 24, "bold"),
        ).pack(anchor="w")

        # Event heading
        ttk.Label(
            self.content,
            text=f"Event: {event.get('event_name', 'Unnamed Event')}",
            font=("Arial", 11),
        ).pack(anchor="w", pady=(5, 20))

        # Event details and trader notes row
        details_row = ttk.Frame(self.content)

        details_row.pack(
            fill="x",
            pady=(0, 10),
        )

        details_row.columnconfigure(0, weight=1)
        details_row.columnconfigure(1, weight=2)

        # -------------------------
        # Event information panel
        # -------------------------
        event_info_frame = ttk.LabelFrame(
            details_row,
            text="Event Details",
            padding=8,
        )

        event_info_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 8),
        )

        start_time = event.get("start_time") or "Not set"

        event_status = (
            event.get("status", "draft").title()
            if event.get("active", True)
            else "Suspended"
        )

        category = event.get("category") or "Not set"
        suspend_mode = event.get("suspend_mode", "AUTO")

        publish_status = (
            "Published"
            if event.get("published", False)
            else "Unpublished"
        )

        publish_button_text = (
            "Unpublish Event"
            if event.get("published", False)
            else "Publish Event"
        )

        ttk.Label(
            event_info_frame,
            text=f"Category: {category}",
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, 20),
            pady=3,
        )

        ttk.Label(
            event_info_frame,
            text=f"Status: {event_status}",
        ).grid(
            row=0,
            column=1,
            sticky="w",
            pady=3,
        )

        ttk.Label(
            event_info_frame,
            text=f"Start time: {start_time}",
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=(0, 20),
            pady=3,
        )

        ttk.Label(
            event_info_frame,
            text=f"Auto suspend: {suspend_mode}",
        ).grid(
            row=1,
            column=1,
            sticky="w",
            pady=3,
        )

        ttk.Label(
            event_info_frame,
            text=f"Publish: {publish_status}",
        ).grid(
            row=2,
            column=0,
            sticky="w",
            pady=3,
        )

        event_button_frame = ttk.Frame(event_info_frame)

        event_button_frame.grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(6, 0),
        )

        ttk.Button(
            event_button_frame,
            text="Edit Event Details",
            command=lambda: self.edit_event_details(
                event,
                market,
            ),
        ).pack(
            side="left",
        )

        ttk.Button(
            event_button_frame,
            text=publish_button_text,
            command=lambda: self.toggle_event_publish_from_market(
                event,
                market,
            ),
        ).pack(
            side="left",
            padx=(8, 0),
        )

        # -------------------------
        # Trader notes panel
        # -------------------------
        notes_frame = ttk.LabelFrame(
            details_row,
            text="Trader Notes",
            padding=8,
        )

        notes_frame.grid(
            row=0,
            column=1,
            sticky="nsew",
        )

        self.trader_notes_text = tk.Text(
            notes_frame,
            height=3,
            wrap="word",
        )

        self.trader_notes_text.pack(
            fill="both",
            expand=True,
        )

        self.trader_notes_text.insert(
            "1.0",
            event.get("trader_notes", ""),
        )

        ttk.Button(
            notes_frame,
            text="Save Notes",
            command=lambda: self.save_trader_notes(
                event,
                market,
            ),
        ).pack(
            anchor="e",
            pady=(6, 0),
        )


        # Container for the trading grid

        market_summary_frame = ttk.Frame(self.content)
        market_summary_frame.pack(fill="x", pady=(0, 12))

        self.overround_label = ttk.Label(
            market_summary_frame,
            text="Overround: 0.00%",
            font=("Arial", 14, "bold"),
        )

        self.overround_label.pack(side="left")
        self.update_market_overround(market)

        action_frame = ttk.Frame(self.content)
        action_frame.pack(fill="x", pady=(0, 10))

        market_is_suspended = (
            str(market.get("status", "ACTIVE")).upper()
            == "SUSPENDED"
        )

        market_button_text = (
            "Unsuspend Market"
            if market_is_suspended
            else "Suspend Market"
        )

        ttk.Button(
            action_frame,
            text="Save Changes",
            command=lambda: self.save_pending_prices(
                event,
                market,
            ),
        ).pack(side="left")

        ttk.Button(
            action_frame,
            text="Discard Changes",
            command=lambda: self.discard_pending_prices(
                event,
                market,
            ),
        ).pack(side="left", padx=(8, 0))

        ttk.Button(
            action_frame,
            text=market_button_text,
            command=lambda: self.toggle_market_suspension(
                event,
                market,
            ),
        ).pack(side="left", padx=(20, 0))

        price_history_button = ttk.Button(
            action_frame,
            text="Price History",
            command=lambda: self.show_price_history_popup(
                market,
            ),
        )

        price_history_button.pack(
            side="left",
            padx=(8, 0),
        )

        manage_selections_button = ttk.Button(
            action_frame,
            text="Manage Selections",
            command=lambda: self.show_manage_selections_popup(
                event,
                market,
            ),
        )

        manage_selections_button.pack(
            side="left",
            padx=(8, 0),
        )

        settle_market_button = ttk.Button(
            action_frame,
            text="Settle Market",
            command=lambda: self.show_settlement_popup(
                event,
                market,
            ),
        )

        settle_market_button.pack(
            side="left",
            padx=(8, 0),
        )

        market_publish_button_text = (
            "Unpublish Market"
            if market.get("published", False)
            else "Publish Market"
        )

        ttk.Button(
            action_frame,
            text=market_publish_button_text,
            command=lambda: self.toggle_market_publish(
                event,
                market,
            ),
        ).pack(
            side="left",
            padx=(5, 0),
        )

        table_frame = ttk.Frame(self.content)
        table_frame.pack(fill="both", expand=True)

        columns = (
            "selection", 
            "price",
            "probability",
            "shorten",
            "lengthen",
            "status",
            "display",
        )

        selection_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=14,
        )

        self.selection_table = selection_table

        selection_table.heading("selection", text="Selection")
        selection_table.heading("price", text="Price")
        selection_table.heading("probability", text="Probability")
        selection_table.heading("shorten", text="▼")
        selection_table.heading("lengthen", text="▲")
        selection_table.heading("status", text="Status")
        selection_table.heading("display", text="Display")
        selection_table.column(
            "selection",
            width=420,
            minwidth=200,
            anchor="w",
        )
        selection_table.column(
            "price",
            width=140,
            minwidth=100,
            anchor="center",
        )
        selection_table.column(
            "probability",
            width=90,
            minwidth=80,
            anchor="center",
        )
        selection_table.column(
            "shorten",
            width=90,
            minwidth=70,
            anchor="center",
            stretch=False,
        )
        selection_table.column(
            "lengthen",
            width=90,
            minwidth=70,
            anchor="center",
            stretch=False,
        )
        selection_table.column(
            "status",
            width=140,
            minwidth=100,
            anchor="center",
        )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=selection_table.yview,
        )

        selection_table.configure(yscrollcommand=scrollbar.set)

        selection_table.pack(
            side="left",
            fill="both",
            expand=True,
        )
        scrollbar.pack(
            side="right",
            fill="y",
        )

        selection_table.tag_configure(
            "pending",
            background="#fff4cc",
            foreground="#5c4a00",
        )

        selection_table.tag_configure(
            "suspended",
            background="#fbeaea",
            foreground="#8a2d2d",
        )

        selection_table.tag_configure(
            "winner",
            background="#e5f4e5",
            foreground="#246b24",
        )

        selection_table.tag_configure(
            "loser",
            background="#f2f2f2",
            foreground="#666666",
        )

        selection_table.tag_configure(
            "void",
            background="#fff3d6",
            foreground="#7a5a00",
        )

        # Add the real selections from the backend
        for selection_index, selection in enumerate(
            market.get("selections", [])
        ):
            pending_key = (id(market), selection_index)

            price = self.pending_prices.get(
                pending_key,
                selection.get("price", [0, 1]),
            )

            if isinstance(price, (list, tuple)) and len(price) == 2:
                price_text = f"{price[0]}/{price[1]}"
            else:
                price_text = str(price)

            if isinstance(price, (list, tuple)) and len(price) == 2:
                probability_value = probability(
                    price[0],
                    price[1],
                )
                probability_text = f"{probability_value:.2f}%"
            else:
                probability_text = "-"

            is_pending = pending_key in self.pending_prices
            selection_is_active = selection.get("active", True)
            market_is_suspended = (
                str(market.get("status", "ACTIVE")).upper()
                == "SUSPENDED"
            )

            result = selection.get("result", "")

            if result == "Won":
                status_text = "Won"
            elif result == "Lost":
                status_text = "Lost"
            elif result == "Void":
                status_text = "Void"
            elif market_is_suspended:
                status_text = "Suspended"
            elif not selection_is_active:
                status_text = "Suspended"
            elif is_pending:
                status_text = "Pending"
            else:
                status_text = "Active"

            if result == "Won":
                row_tag = "winner"
            elif result == "Lost":
                row_tag = "loser"
            elif result == "Void":
                row_tag = "void"
            elif market_is_suspended or not selection_is_active:
                row_tag = "suspended"
            elif is_pending:
                row_tag = "pending"
            else:
                row_tag = ""

            display_text = (
                "Displayed"
                if selection.get("displayed", True)
                else "Non Display"
            )

            selection_table.insert(
                "",
                "end",
                iid=str(selection_index),
                values=(
                    selection.get("name", "Unnamed Selection"),
                    price_text,
                    probability_text,
                    "▼",
                    "▲",
                    status_text,
                    display_text,
                ),
                tags=(row_tag,) if row_tag else (),
            )
        selection_table.bind(
            "<Double-1>",
            lambda event_click: self.edit_price_cell(
                event_click,
                selection_table,
                event,
                market,
            ),
        )
        selection_table.bind(
            "<ButtonRelease-1>",
            lambda event_click: self.handle_price_tick_click(
                event_click,
                selection_table,
                event,
                market,
            ),
        )

    def edit_event_details(self, event, market):
        popup = tk.Toplevel(self.root)
        popup.title("Edit Event Details")
        popup.geometry("480x350")
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.grab_set()

        form_frame = ttk.Frame(
            popup,
            padding=20,
        )
        form_frame.pack(
            fill="both",
            expand=True,
        )

        # Event name
        ttk.Label(
            form_frame,
            text="Event name",
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=8,
        )

        event_name_var = tk.StringVar(
            value=event.get("event_name", "")
        )

        ttk.Entry(
            form_frame,
            textvariable=event_name_var,
            width=36,
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(15, 0),
            pady=8,
        )

        # Start date and time
        ttk.Label(
            form_frame,
            text="Start date/time",
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=8,
        )

        start_time_var = tk.StringVar(
            value=event.get("start_time", "")
        )

        ttk.Entry(
            form_frame,
            textvariable=start_time_var,
            width=36,
        ).grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(15, 0),
            pady=8,
        )

        ttk.Label(
            form_frame,
            text="Use format: DD/MM/YYYY HH:MM",
        ).grid(
            row=2,
            column=1,
            sticky="w",
            padx=(15, 0),
        )

        # Status
        ttk.Label(
            form_frame,
            text="Status",
        ).grid(
            row=3,
            column=0,
            sticky="w",
            pady=8,
        )

        status_var = tk.StringVar(
            value=event.get("status", "draft").title()
        )

        status_box = ttk.Combobox(
            form_frame,
            textvariable=status_var,
            values=[
                "Draft",
                "Trading",
                "Suspended",
                "Settled",
            ],
            state="readonly",
            width=33,
        )
        status_box.grid(
            row=3,
            column=1,
            sticky="ew",
            padx=(15, 0),
            pady=8,
        )

        # Auto suspend mode
        ttk.Label(
            form_frame,
            text="Suspend mode",
        ).grid(
            row=4,
            column=0,
            sticky="w",
            pady=8,
        )

        suspend_mode_var = tk.StringVar(
            value=event.get("suspend_mode", "AUTO")
        )

        suspend_mode_box = ttk.Combobox(
            form_frame,
            textvariable=suspend_mode_var,
            values=[
                "AUTO",
                "MANUAL",
            ],
            state="readonly",
            width=33,
        )
        suspend_mode_box.grid(
            row=4,
            column=1,
            sticky="ew",
            padx=(15, 0),
            pady=8,
        )

        def save_event_details():
            event_name = event_name_var.get().strip()
            start_time = start_time_var.get().strip()

            parsed_start_time = None

            if start_time:
                try:
                    parsed_start_time = datetime.strptime(
                        start_time,
                        "%d/%m/%Y %H:%M",
                    )
                except ValueError:
                    messagebox.showwarning(
                        "Event Details",
                        "Start date/time must use DD/MM/YYYY HH:MM.",
                        parent=popup,
                    )
                    return

            if not event_name:
                messagebox.showwarning(
                    "Event Details",
                    "Event name cannot be blank.",
                    parent=popup,
                )
                return

            event["event_name"] = event_name
            event["start_time"] = (
                parsed_start_time.strftime("%d/%m/%Y %H:%M")
                if parsed_start_time
                else ""
            )
            selected_status = status_var.get()

            event["status"] = selected_status
            event["suspend_mode"] = suspend_mode_var.get()

            if selected_status == "Suspended":
                event["active"] = False
            elif selected_status in ("Trading", "Draft"):
                event["active"] = True

            touch_event(event)
            save_platform(self.platform)

            popup.destroy()
            self.show_market_screen(event, market)

        button_frame = ttk.Frame(form_frame)
        button_frame.grid(
            row=5,
            column=0,
            columnspan=2,
            sticky="e",
            pady=(25, 0),
        )

        ttk.Button(
            button_frame,
            text="Cancel",
            command=popup.destroy,
        ).pack(
            side="right",
            padx=(8, 0),
        )

        ttk.Button(
            button_frame,
            text="Save",
            command=save_event_details,
        ).pack(
            side="right",
        )

        form_frame.columnconfigure(
            1,
            weight=1,
        )

    def show_manage_selections_popup(
        self,
        event,
        market,
    ):
        popup = tk.Toplevel(self.root)
        popup.title("Manage Selections")
        popup.geometry("650x500")
        popup.transient(self.root)
        popup.grab_set()

        title_label = ttk.Label(
            popup,
            text=f"Manage Selections - {market.get('name', 'Market')}",
            font=("Arial", 15, "bold"),
        )
        title_label.pack(
            anchor="w",
            padx=20,
            pady=(18, 12),
        )

        form_frame = ttk.Frame(popup)
        form_frame.pack(
            fill="x",
            padx=20,
            pady=(0, 15),
        )

        ttk.Label(
            form_frame,
            text="Selection Name",
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, 10),
        )

        name_entry = ttk.Entry(
            form_frame,
            width=32,
        )
        name_entry.grid(
            row=1,
            column=0,
            sticky="w",
            padx=(0, 10),
        )

        ttk.Label(
            form_frame,
            text="Price",
        ).grid(
            row=0,
            column=1,
            sticky="w",
            padx=(0, 10),
        )

        price_entry = ttk.Entry(
            form_frame,
            width=12,
        )
        price_entry.grid(
            row=1,
            column=1,
            sticky="w",
            padx=(0, 10),
        )

        selections_table = ttk.Treeview(
            popup,
            columns=(
                "selection",
                "price",
                "status",
            ),
            show="headings",
            height=14,
        )

        selections_table.heading(
            "selection",
            text="Selection",
        )
        selections_table.heading(
            "price",
            text="Price",
        )
        selections_table.heading(
            "status",
            text="Status",
        )

        selections_table.column(
            "selection",
            width=330,
            anchor="w",
        )
        selections_table.column(
            "price",
            width=100,
            anchor="center",
        )
        selections_table.column(
            "status",
            width=130,
            anchor="center",
        )

        selections_table.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 15),
        )

        def refresh_table():
            for row in selections_table.get_children():
                selections_table.delete(row)

            sorted_selections = sorted(
                market.get("selections", []),
                key=lambda selection: probability(
                    selection["price"][0],
                    selection["price"][1],
                ),
                reverse=True,
            )

            for selection in sorted_selections:
                price = selection.get(
                    "price",
                    [0, 1],
                )

                price_text = f"{price[0]}/{price[1]}"

                if not selection.get("active", True):
                    status_text = "Suspended"
                elif not selection.get("displayed", True):
                    status_text = "Non Display"
                else:
                    status_text = "Active"

                selections_table.insert(
                    "",
                    "end",
                    values=(
                        selection.get(
                            "name",
                            "Unnamed Selection",
                        ),
                        price_text,
                        status_text,
                    ),
                )

        def add_new_selection():
            selection_name = name_entry.get().strip()
            price_text = price_entry.get().strip()

            if not selection_name:
                messagebox.showwarning(
                    "Add Selection",
                    "Enter a selection name.",
                )
                return

            if "/" not in price_text:
                messagebox.showwarning(
                    "Add Selection",
                    "Enter the price as fractional odds, for example 5/1.",
                )
                return

            try:
                numerator_text, denominator_text = price_text.split(
                    "/",
                    1,
                )

                numerator = int(numerator_text)
                denominator = int(denominator_text)

                if numerator <= 0 or denominator <= 0:
                    raise ValueError

            except ValueError:
                messagebox.showwarning(
                    "Add Selection",
                    "Enter a valid fractional price, for example 5/1.",
                )
                return

            add_selection(
                market,
                selection_name,
                [
                    numerator,
                    denominator,
                ],
            )

            market["selections"].sort(
                key=lambda selection: probability(
                    selection["price"][0],
                    selection["price"][1],
                ),
                reverse=True,
            )

            save_platform(self.platform)

            name_entry.delete(0, "end")
            price_entry.delete(0, "end")

            refresh_table()

            self.show_market_screen(
                event,
                market,
            )

        add_button = ttk.Button(
            form_frame,
            text="Add Selection",
            command=add_new_selection,
        )
        add_button.grid(
            row=1,
            column=2,
            sticky="w",
        )

        close_button = ttk.Button(
            popup,
            text="Close",
            command=popup.destroy,
        )
        close_button.pack(
            pady=(0, 18),
        )

        refresh_table()
        name_entry.focus_set()

    def show_settlement_popup(
        self,
        event,
        market,
    ):
        popup = tk.Toplevel(self.root)
        popup.title(f"Settle Market - {market.get('name', 'Market')}")
        popup.geometry("700x560")
        popup.transient(self.root)
        popup.grab_set()

        pending_results = {}

        title_label = ttk.Label(
            popup,
            text=f"Settle Market - {market.get('name', 'Market')}",
            font=("Arial", 15, "bold"),
        )
        title_label.pack(
            anchor="w",
            padx=20,
            pady=(18, 12),
        )

        bulk_frame = ttk.Frame(popup)
        bulk_frame.pack(
            fill="x",
            padx=20,
            pady=(0, 12),
        )

        ttk.Label(
            bulk_frame,
            text="Bulk result:",
            font=("Arial", 10, "bold"),
        ).pack(
            side="left",
            padx=(0, 10),
        )

        table = ttk.Treeview(
            popup,
            columns=(
                "selection",
                "result",
                "win",
                "lose",
                "void",
            ),
            show="headings",
            height=16,
        )

        table.heading("selection", text="Selection")
        table.heading("result", text="Result")
        table.heading("win", text="W")
        table.heading("lose", text="L")
        table.heading("void", text="V")

        table.column(
            "selection",
            width=330,
            anchor="w",
        )
        table.column(
            "result",
            width=120,
            anchor="center",
        )
        table.column(
            "win",
            width=55,
            anchor="center",
        )
        table.column(
            "lose",
            width=55,
            anchor="center",
        )
        table.column(
            "void",
            width=55,
            anchor="center",
        )

        table.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 15),
        )

        def get_display_result(selection):
            selection_id = selection.get("id")

            if selection_id in pending_results:
                return pending_results[selection_id]

            return selection.get("result", "")

        def refresh_table():
            for row in table.get_children():
                table.delete(row)

            for selection_index, selection in enumerate(
                market.get("selections", [])
            ):
                result_text = get_display_result(selection)

                table.insert(
                    "",
                    "end",
                    iid=str(selection_index),
                    values=(
                        selection.get("name", "Unnamed Selection"),
                        result_text or "Unsettled",
                        "W",
                        "L",
                        "V",
                    ),
                )

        def set_individual_result(
            selection_index,
            result_value,
        ):
            selections = market.get("selections", [])

            if selection_index >= len(selections):
                return

            selection = selections[selection_index]
            selection_id = selection.get("id")

            pending_results[selection_id] = result_value
            refresh_table()

        def apply_bulk_result(result_value):
            for selection in market.get("selections", []):
                selection_id = selection.get("id")

                # Individual pending settlement takes priority.
                if selection_id in pending_results:
                    continue

                # Existing saved settlement also takes priority.
                if selection.get("result", ""):
                    continue

                pending_results[selection_id] = result_value

            refresh_table()

        def handle_table_click(event_click):
            region = table.identify_region(
                event_click.x,
                event_click.y,
            )

            if region != "cell":
                return

            row_id = table.identify_row(event_click.y)
            column_id = table.identify_column(event_click.x)

            if not row_id:
                return

            selection_index = int(row_id)

            if column_id == "#3":
                set_individual_result(
                    selection_index,
                    "Won",
                )

            elif column_id == "#4":
                set_individual_result(
                    selection_index,
                    "Lost",
                )

            elif column_id == "#5":
                set_individual_result(
                    selection_index,
                    "Void",
                )

        def clear_pending_results():
            pending_results.clear()
            refresh_table()

        def save_settlement():
            if not pending_results:
                messagebox.showinfo(
                    "Settle Market",
                    "No settlement changes have been selected.",
                )
                return

            unsettled_selections = [
                selection
                for selection in market.get("selections", [])
                if (
                    not selection.get("result", "")
                    and selection.get("id") not in pending_results
                )
            ]

            if unsettled_selections:
                proceed = messagebox.askyesno(
                    "Incomplete Settlement",
                    "Some selections are still unsettled. Save anyway?",
                )

                if not proceed:
                    return

            confirmed = messagebox.askyesno(
                "Confirm Settlement",
                "Save these market results?",
            )

            if not confirmed:
                return

            print("Saving settlement:", pending_results)

            old_results = {
                selection.get("id"): selection.get("result", "")
                for selection in market.get("selections", [])
            }

            settle_market_results(
                self.platform,
                [],
                event,
                market,
                pending_results,
            )

            result_changes = []

            for selection in market.get("selections", []):
                selection_id = selection.get("id")
                old_result = old_results.get(selection_id, "")
                new_result = selection.get("result", "")

                if old_result != new_result:
                    result_changes.append({
                        "selection_id": selection_id,
                        "selection_name": selection.get("name"),
                        "old_result": old_result,
                        "new_result": new_result,
                    })

            all_markets_settled = all(
                all(
                    selection.get("result", "")
                    for selection in market_item.get("selections", [])
                )
                for market_item in event.get("markets", [])
            )

            if all_markets_settled:
                event["archived"] = True
            touch_event(
                event,
                change_type="settlement",
                details={
                    "market_id": market.get("id"),
                    "market_name": market.get("name"),
                    "changes": result_changes,
                    "event_archived": event.get("archived", False),
                },
            )
            save_platform(self.platform)


            print(
                "Saved results:",
                [
                    (
                        selection.get("name"),
                        selection.get("result"),
                    )
                    for selection in market.get("selections", [])
                ],
            )

            popup.destroy()

            self.show_market_screen(
                event,
                market,
            )

        ttk.Button(
            bulk_frame,
            text="W",
            command=lambda: apply_bulk_result("Won"),
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            bulk_frame,
            text="L",
            command=lambda: apply_bulk_result("Lost"),
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            bulk_frame,
            text="V",
            command=lambda: apply_bulk_result("Void"),
        ).pack(
            side="left",
            padx=3,
        )

        button_frame = ttk.Frame(popup)
        button_frame.pack(
            fill="x",
            padx=20,
            pady=(0, 18),
        )

        ttk.Button(
            button_frame,
            text="Clear Pending",
            command=clear_pending_results,
        ).pack(side="left")

        ttk.Button(
            button_frame,
            text="Save Settlement",
            command=save_settlement,
        ).pack(
            side="right",
            padx=(8, 0),
        )

        ttk.Button(
            button_frame,
            text="Close",
            command=popup.destroy,
        ).pack(side="right")

        table.bind(
            "<Button-1>",
            handle_table_click,
        )

        refresh_table()

    def show_price_history_popup(
        self,
        market,
    ):
        selected_rows = self.selection_table.selection()

        if not selected_rows:
            messagebox.showinfo(
                "Price History",
                "Select a runner first.",
            )
            return

        row_id = selected_rows[0]

        try:
            selection_index = int(row_id)
            selection = market["selections"][selection_index]
        except (ValueError, IndexError, KeyError):
            messagebox.showerror(
                "Price History",
                "Could not find the selected runner.",
            )
            return

        selection_name = selection.get(
            "name",
            "Unnamed Selection",
        )

        current_price = selection.get(
            "price",
            [0, 1],
        )

        current_price_text = (
            f"{current_price[0]}/{current_price[1]}"
        )

        popup = tk.Toplevel(self.root)
        popup.title(f"Price History - {selection_name}")
        popup.geometry("500x430")
        popup.transient(self.root)
        popup.grab_set()

        title_label = ttk.Label(
            popup,
            text=selection_name,
            font=("Arial", 16, "bold"),
        )
        title_label.pack(
            anchor="w",
            padx=20,
            pady=(18, 4),
        )

        current_price_label = ttk.Label(
            popup,
            text=f"Current Price: {current_price_text}",
            font=("Arial", 11, "bold"),
        )
        current_price_label.pack(
            anchor="w",
            padx=20,
            pady=(0, 14),
        )

        history_table = ttk.Treeview(
            popup,
            columns=(
                "date",
                "time",
                "price",
            ),
            show="headings",
            height=12,
        )

        history_table.heading(
            "date",
            text="Date",
        )
        history_table.heading(
            "time",
            text="Time",
        )
        history_table.heading(
            "price",
            text="Price",
        )

        history_table.column(
            "date",
            width=150,
            anchor="center",
        )
        history_table.column(
            "time",
            width=150,
            anchor="center",
        )
        history_table.column(
            "price",
            width=100,
            anchor="center",
        )

        history_table.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 14),
        )

        price_history = selection.get(
            "price_history",
            [],
        )

        for entry in reversed(price_history):
            created = str(
                entry.get("time", "")
            )

            date_text = ""
            time_text = ""

            if "T" in created:
                date_text, time_text = created.split(
                    "T",
                    1,
                )
            elif " " in created:
                date_text, time_text = created.split(
                    " ",
                    1,
                )
            else:
                date_text = created

            time_text = time_text.split(".")[0]

            price = entry.get(
                "new_price",
                ["-", "-"],
            )

            if (
                isinstance(price, (list, tuple))
                and len(price) == 2
            ):
                price_text = f"{price[0]}/{price[1]}"
            else:
                price_text = str(price)

            history_table.insert(
                "",
                "end",
                values=(
                    date_text,
                    time_text,
                    price_text,
                ),
            )

        if not price_history:
            history_table.insert(
                "",
                "end",
                values=(
                    "No price history",
                    "",
                    "",
                ),
            )

        close_button = ttk.Button(
            popup,
            text="Close",
            command=popup.destroy,
        )
        close_button.pack(
            pady=(0, 18),
        )

    def update_market_overround(self, market):
        overround = 0.0

        for selection_index, selection in enumerate(
            market.get("selections", [])
        ):
            # Hidden or individually suspended selections do not count.
            if not selection.get("displayed", True):
                continue

            if not selection.get("active", True):
                continue

            result = selection.get("result", "")

            if result in ("Won", "Lost", "Void"):
                continue

            pending_key = (id(market), selection_index)

            price = self.pending_prices.get(
                pending_key,
                selection.get("price", [0, 1]),
            )

            if not isinstance(price, (list, tuple)) or len(price) != 2:
                continue

            numerator = price[0]
            denominator = price[1]

            if numerator <= 0 or denominator <= 0:
                continue

            overround += probability(
                numerator,
                denominator,
            )

        self.overround_label.config(
            text=f"Overround: {overround:.2f}%"
        )

    def save_pending_prices(self, event, market):
        changes_saved = False

        price_changes = []

        for selection_index, selection in enumerate(
            market.get("selections", [])
        ):
            pending_key = (id(market), selection_index)

            if pending_key not in self.pending_prices:
                continue

            new_price = self.pending_prices[pending_key]

            old_price = selection.get("price")

            save_remote_price(
                event.get("id"),
                market.get("id"),
                selection.get("id"),
                new_price[0],
                new_price[1],
            )

            set_price(
                selection,
                new_price[0],
                new_price[1],
            )

            price_changes.append(
                {
                    "market_id": market.get("id"),
                    "market_name": market.get("name"),
                    "selection_id": selection.get("id"),
                    "selection_name": selection.get("name"),
                    "old_price": old_price,
                    "new_price": selection.get("price"),
                }
            )

            del self.pending_prices[pending_key]
            changes_saved = True

        if changes_saved:
            market["selections"].sort(
                key=lambda selection: probability(
                    selection["price"][0],
                    selection["price"][1],
                ),
                reverse=True,
            )

            touch_event(
                event,
                change_type="price_change",
                details={
                    "market_id": market.get("id"),
                    "market_name": market.get("name"),
                    "changes": price_changes,
                },
            )
            save_platform(self.platform)

        self.show_market_screen(event, market)

    def discard_pending_prices(self, event, market):
        keys_to_remove = []

        for pending_key in self.pending_prices:
            if pending_key[0] == id(market):
                keys_to_remove.append(pending_key)

        for pending_key in keys_to_remove:
            del self.pending_prices[pending_key]

        self.show_market_screen(event, market)

    def toggle_market_publish(
        self,
        event,
        market,
    ):
        market["published"] = not market.get(
            "published",
            False,
        )

        touch_event(event)
        save_platform(self.platform)

        self.show_market_screen(
            event,
            market,
        )

    def handle_price_tick_click(
        self,
        event_click,
        selection_table,
        event,
        market,
    ):
        row_id = selection_table.identify_row(event_click.y)
        column_id = selection_table.identify_column(event_click.x)

        if not row_id:
            return

        # #3 = down/shorten
        # #4 = up/lengthen
        # #3 = down/shorten
        # #4 = up/lengthen
        # #5 = status toggle
        if column_id not in ("#4", "#5", "#6", "#7"):
            return

        try:
            selection_index = int(row_id)
            selection = market["selections"][selection_index]

            if column_id == "#6":
                self.toggle_selection_suspension(
                    event,
                    market,
                    selection,
                )
                return

            if column_id == "#7":
                self.toggle_selection_display(
                    event,
                    market,
                    selection,
                )
                return

            pending_key = (id(market), selection_index)

            current_price = self.pending_prices.get(
                pending_key,
                selection["price"],
            )

            current_price = list(current_price)
            ladder_index = PRICE_LADDER.index(current_price)

            if column_id == "#4":
                # Down arrow: shorten the price.
                if ladder_index == 0:
                    return

                new_price = PRICE_LADDER[ladder_index - 1]

            else:
                # Up arrow: lengthen the price.
                if ladder_index >= len(PRICE_LADDER) - 1:
                    return

                new_price = PRICE_LADDER[ladder_index + 1]

            self.pending_prices[pending_key] = list(new_price)

            selection_table.set(
                row_id,
                "price",
                f"{new_price[0]}/{new_price[1]}",
            )

            new_probability = probability(
                new_price[0],
                new_price[1],
            )

            selection_table.set(
                row_id,
                "probability",
                f"{new_probability:.2f}%",
            )

            selection_table.set(
                row_id,
                "status",
                "Pending",
            )

            selection_table.item(
                row_id,
                tags=("pending,"),
            )

            self.update_market_overround(market)

        except ValueError:
            messagebox.showerror(
                "Price ladder error",
                "This selection's current price is not on the price ladder.",
            )

        except (TypeError, KeyError, IndexError):
            messagebox.showerror(
                "Price update failed",
                "The selection price could not be updated.",
            )

    def toggle_selection_suspension(
        self,
        event,
        market,
        selection,
    ):
        event_name = event.get("event_name", "")
        market_name = market.get("name", "")
        selection_name = selection.get("name", "")

        old_active = selection.get("active", True)

        try:
            if selection.get("active", True):
                suspend_platform_selection(
                    self.platform,
                    event_name,
                    market_name,
                    selection_name,
                )

                add_audit_log(
                    f"{selection_name} suspended in "
                    f"{event_name} / {market_name}"
                )

            else:
                unsuspend_platform_selection(
                    self.platform,
                    event_name,
                    market_name,
                    selection_name,
                )

                add_audit_log(
                    f"{selection_name} unsuspended in "
                    f"{event_name} / {market_name}"
                )

            save_remote_selection_state(
                event.get("id"),
                market.get("id"),
                selection.get("id"),
                active=selection.get("active", True),
            )

            touch_event(
                event,
                change_type="selection_suspension",
                details={
                    "market_id": market.get("id"),
                    "market_name": market.get("name"),
                    "selection_id": selection.get("id"),
                    "selection_name": selection.get("name"),
                    "old_active": old_active,
                    "new_active": selection.get("active", True),
                },
            )
            save_platform(self.platform)

        except (TypeError, KeyError):
            messagebox.showerror(
                "Suspension failed",
                "The selection status could not be updated.",
            )
            return

        self.show_market_screen(event, market)

    def toggle_selection_display(
        self,
        event,
        market,
        selection,
    ):
        old_displayed = selection.get("displayed", True)
        new_displayed = not old_displayed

        selection["displayed"] = new_displayed

        save_remote_selection_state(
            event.get("id"),
            market.get("id"),
            selection.get("id"),
            displayed=new_displayed,
        )

        touch_event(
            event,
            change_type="selection_display",
            details={
                "market_id": market.get("id"),
                "market_name": market.get("name"),
                "selection_id": selection.get("id"),
                "selection_name": selection.get("name"),
                "old_displayed": old_displayed,
                "new_displayed": new_displayed,
            },
        )

        save_platform(self.platform)

        self.show_market_screen(
            event,
            market,
        )

    def save_trader_notes(self, event, market):
        notes = self.trader_notes_text.get(
            "1.0",
            "end-1c",
        ).strip()

        event["trader_notes"] = notes

        touch_event(event)
        save_platform(self.platform)

        messagebox.showinfo(
            "Trader Notes",
            "Notes saved.",
        )

        self.show_market_screen(
            event,
            market,
        )

    def toggle_market_suspension(
        self,
        event,
        market,
    ):
        event_name = event.get("event_name", "")
        market_name = market.get("name", "")

        market_is_suspended = (
            str(market.get("status", "ACTIVE")).upper()
            == "SUSPENDED"
        )

        try:
            if market_is_suspended:
                unsuspend_platform_market(
                    self.platform,
                    event_name,
                    market_name,
                )

                add_audit_log(
                    f"{market_name} unsuspended in {event_name}"
                )

            else:
                suspend_platform_market(
                    self.platform,
                    event_name,
                    market_name,
                )

                add_audit_log(
                    f"{market_name} suspended in {event_name}"
                )

            save_platform(self.platform)

        except (TypeError, KeyError):
            messagebox.showerror(
                "Market suspension failed",
                "The market status could not be updated.",
            )
            return

        self.show_market_screen(event, market)

    def suspend_event_for_schedule(self, event):
        if event.get("active", True) is False:
            return False

        event["active"] = False

        save_remote_event_state(
            event.get("id"),
            False,
        )

        touch_event(event)
        save_platform(self.platform)

        add_audit_log(
            f"{event.get('event_name', 'Unnamed Event')} "
            "automatically suspended at start time"
        )

        return True

    def check_scheduled_events(self):
        now = datetime.now()

        for event in self.platform:
            if str(
                event.get("suspend_mode", "")
            ).upper() != "AUTO":
                continue

            if event.get("active", True) is False:
                continue

            start_time_text = str(
                event.get("start_time", "")
            ).strip()

            if not start_time_text:
                continue

            try:
                start_time = datetime.strptime(
                    start_time_text,
                    "%d/%m/%Y %H:%M",
                )
            except ValueError:
                continue

            if now >= start_time:
                event["active"] = False
                touch_event(event)
                save_platform(self.platform)

        self.root.after(
            1000,
            self.check_scheduled_events,
        )

    def archive_old_events(self):
        cutoff = datetime.now() - timedelta(days=28)

        changed = False

        for event in self.platform:
            if event.get("archived", False):
                continue

            start_time = event.get("start_time", "").strip()

            if not start_time:
                continue

            try:
                event_start = datetime.strptime(
                    start_time,
                    "%d/%m/%Y %H:%M",
                )
            except ValueError:
                continue

            if event_start <= cutoff:
                event["archived"] = True

                touch_event(event)

                changed = True

        if changed:
            save_platform(self.platform)

    def edit_price_cell(
        self,
        event_click,
        selection_table,
        event,
        market,
    ):
        row_id = selection_table.identify_row(event_click.y)
        column_id = selection_table.identify_column(event_click.x)

        # Only allow editing in the Price column.
        if not row_id or column_id != "#2":
            return

        cell_box = selection_table.bbox(row_id, column_id)

        if not cell_box:
            return

        x, y, width, height = cell_box

        current_values = selection_table.item(row_id, "values")
        current_price = current_values[1]

        price_entry = ttk.Entry(selection_table)
        price_entry.insert(0, current_price)

        price_entry.place(
            x=x,
            y=y,
            width=width,
            height=height,
        )

        price_entry.focus_set()
        price_entry.select_range(0, tk.END)

        price_entry.bind(
            "<Return>",
            lambda _event: self.save_edited_price(
                price_entry,
                row_id,
                event,
                market,
            ),
        )

        price_entry.bind(
            "<Escape>",
            lambda _event: price_entry.destroy(),
        )

        price_entry.bind(
            "<FocusOut>",
            lambda _event: price_entry.destroy(),
        )

    def save_edited_price(
        self,
        price_entry,
        row_id,
        event,
        market,
    ):
        entered_price = price_entry.get().strip()

        try:
            price_parts = entered_price.split("/")

            if len(price_parts) != 2:
                raise ValueError

            numerator = int(price_parts[0])
            denominator = int(price_parts[1])

            if numerator <= 0 or denominator <= 0:
                raise ValueError

            selection_index = int(row_id)
            selection = market["selections"][selection_index]

            set_price(
                selection,
                numerator,
                denominator,
            )

            save_platform(self.platform)

        except (ValueError, TypeError, KeyError, IndexError):
            messagebox.showerror(
                "Invalid price",
                "Enter fractional odds in a format such as 4/6 or 10/1.",
            )

            price_entry.focus_set()
            price_entry.select_range(0, tk.END)
            return

        price_entry.destroy()

        # Rebuild the screen using the newly saved backend price.
        self.show_market_screen(event, market)

    def create_summary_card(self, parent, heading, value):

        card = ttk.LabelFrame(
            parent,
            text=heading,
            padding=20
        )

        card.pack(
            side="left",
            fill="x",
            expand=True,
            padx=5
        )

        ttk.Label(
            card,
            text=value,
            font=("Arial", 24, "bold")
        ).pack()

    def add_event_row(self, parent, event_name, status):

        row = ttk.Frame(parent)
        row.pack(fill="x", pady=6)

        ttk.Button(
            row,
            text=event_name,
            command=lambda name=event_name: self.open_event_placeholder(name)
        ).pack(
            side="left",
            fill="x",
            expand=True
        )

        ttk.Label(
            row,
            text=status,
            width=12,
            anchor="center"
        ).pack(
            side="right",
            padx=(10, 0)
        )

    def show_import_centre(self):
        self.clear_content()

        ttk.Label(
            self.content,
            text="Event Builder",
            font=("Arial", 20, "bold"),
        ).pack(
            anchor="w",
            pady=(0, 8),
        )

        manual_frame = ttk.LabelFrame(
            self.content,
            text="Manual Creation",
            padding=15,
        )

        manual_frame.pack(
            fill="x",
            pady=(0, 15),
        )

        ttk.Label(
            manual_frame,
            text="Create an event manually, then add markets and selections.",
        ).pack(
            anchor="w",
            pady=(0, 10),
        )

        ttk.Button(
            manual_frame,
            text="Create Event",
            command=self.create_event_popup,
        ).pack(
            anchor="w",
        )

        ttk.Label(
            self.content,
            text=(
                "Import one event and one pre-match market "
                "from an Excel pricing worksheet."
            ),
        ).pack(
            anchor="w",
            pady=(0, 20),
        )

        file_frame = ttk.Frame(self.content)
        file_frame.pack(
            fill="x",
            pady=(0, 15),
        )

        self.import_file_path = tk.StringVar()

        file_entry = ttk.Entry(
            file_frame,
            textvariable=self.import_file_path,
            state="readonly",
            width=70,
        )
        file_entry.pack(
            side="left",
            fill="x",
            expand=True,
        )

        ttk.Button(
            file_frame,
            text="Choose Excel File",
            command=self.choose_excel_import_file,
        ).pack(
            side="left",
            padx=(8, 0),
        )

        self.import_preview_frame = ttk.LabelFrame(
            self.content,
            text="Import Preview",
        )
        self.import_preview_frame.pack(
            fill="both",
            expand=True,
            pady=(0, 15),
        )

        ttk.Label(
            self.import_preview_frame,
            text="Choose an Excel file to preview it.",
        ).pack(
            anchor="w",
            padx=15,
            pady=15,
        )

        ttk.Button(
            self.content,
            text="Import Event",
            command=self.import_excel_event,
        ).pack(
            anchor="w",
            padx=15,
            pady=(0, 15),
        )

    def create_event_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Create Event")
        popup.geometry("480x420")
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.grab_set()

        form = ttk.Frame(
            popup,
            padding=20,
        )
        form.pack(
            fill="both",
            expand=True,
        )

        name_var = tk.StringVar()
        category_var = tk.StringVar()
        class_var = tk.StringVar()
        type_var = tk.StringVar()
        start_time_var = tk.StringVar()
        suspend_mode_var = tk.StringVar(value="AUTO")

        fields = [
            ("Event name", name_var),
            ("Category", category_var),
            ("Class", class_var),
            ("Type", type_var),
            ("Start date/time", start_time_var),
        ]

        for row_number, (label, variable) in enumerate(fields):
            ttk.Label(
                form,
                text=label,
            ).grid(
                row=row_number,
                column=0,
                sticky="w",
                pady=8,
            )

            ttk.Entry(
                form,
                textvariable=variable,
                width=35,
            ).grid(
                row=row_number,
                column=1,
                sticky="ew",
                padx=(15, 0),
                pady=8,
            )

        ttk.Label(
            form,
            text="Use format DD/MM/YYYY HH:MM",
            font=("Arial", 9),
        ).grid(
            row=5,
            column=1,
            sticky="w",
            padx=(15, 0),
        )

        ttk.Label(
            form,
            text="Suspend mode",
        ).grid(
            row=6,
            column=0,
            sticky="w",
            pady=8,
        )

        ttk.Combobox(
            form,
            textvariable=suspend_mode_var,
            values=["AUTO", "MANUAL"],
            state="readonly",
            width=32,
        ).grid(
            row=6,
            column=1,
            sticky="ew",
            padx=(15, 0),
            pady=8,
        )

        def save_new_event():
            event_name = name_var.get().strip()
            category = category_var.get().strip()
            event_class = class_var.get().strip()
            event_type = type_var.get().strip()
            start_time = start_time_var.get().strip()

            if not event_name:
                messagebox.showwarning(
                    "Create Event",
                    "Event name cannot be blank.",
                    parent=popup,
                )
                return

            if start_time:
                try:
                    datetime.strptime(
                        start_time,
                        "%d/%m/%Y %H:%M",
                    )
                except ValueError:
                    messagebox.showwarning(
                        "Create Event",
                        "Start time must use DD/MM/YYYY HH:MM.",
                        parent=popup,
                    )
                    return

            event = create_event(
                category,
                event_class,
                event_type,
                event_name,
            )

            event["start_time"] = start_time
            event["suspend_mode"] = suspend_mode_var.get()
            event["active"] = True

            self.platform.append(event)

            save_platform(self.platform)

            popup.destroy()

            add_market = messagebox.askyesno(
                "Event Created",
                f"{event_name} created successfully.\n\n"
                "Would you like to add a market now?",
            )

            if add_market:
                self.create_market_popup(event)
            else:
                self.show_import_centre()


        button_frame = ttk.Frame(form)
        button_frame.grid(
            row=7,
            column=0,
            columnspan=2,
            sticky="e",
            pady=(20, 0),
        )

        ttk.Button(
            button_frame,
            text="Cancel",
            command=popup.destroy,
        ).pack(
            side="right",
            padx=(8, 0),
        )

        ttk.Button(
            button_frame,
            text="Create Event",
            command=save_new_event,
        ).pack(
            side="right",
        )

        form.columnconfigure(
            1,
            weight=1,
        )

    def create_market_popup(self, event):
        popup = tk.Toplevel(self.root)
        popup.title("Add Market")
        popup.geometry("450x260")
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.grab_set()

        form = ttk.Frame(
            popup,
            padding=20,
        )
        form.pack(
            fill="both",
            expand=True,
        )

        ttk.Label(
            form,
            text=f"Event: {event.get('event_name', 'Unknown Event')}",
            font=("Arial", 12, "bold"),
        ).pack(
            anchor="w",
            pady=(0, 20),
        )

        ttk.Label(
            form,
            text="Market name",
        ).pack(
            anchor="w",
        )

        market_name_var = tk.StringVar()

        market_entry = ttk.Entry(
            form,
            textvariable=market_name_var,
            width=40,
        )
        market_entry.pack(
            fill="x",
            pady=(5, 20),
        )

        market_entry.focus_set()

        def save_new_market():
            market_name = market_name_var.get().strip()

            if not market_name:
                messagebox.showwarning(
                    "Add Market",
                    "Market name cannot be blank.",
                    parent=popup,
                )
                return

            market = create_market(
                event,
                market_name,
            )

            touch_event(event)
            save_platform(self.platform)

            popup.destroy()

            add_selections = messagebox.askyesno(
                "Market Created",
                f"{market_name} created successfully.\n\n"
                "Would you like to add selections now?",
            )

            if add_selections:
                self.create_selection_popup(
                    event,
                    market,
                )
            else:
                self.show_import_centre()

        button_frame = ttk.Frame(form)
        button_frame.pack(
            fill="x",
            pady=(10, 0),
        )

        ttk.Button(
            button_frame,
            text="Cancel",
            command=popup.destroy,
        ).pack(
            side="right",
            padx=(8, 0),
        )

        ttk.Button(
            button_frame,
            text="Create Market",
            command=save_new_market,
        ).pack(
            side="right",
        )

    def create_selection_popup(self, event, market):
        popup = tk.Toplevel(self.root)
        popup.title("Add Selections")
        popup.geometry("600x500")
        popup.transient(self.root)
        popup.grab_set()

        main_frame = ttk.Frame(
            popup,
            padding=20,
        )
        main_frame.pack(
            fill="both",
            expand=True,
        )

        ttk.Label(
            main_frame,
            text=event.get(
                "event_name",
                "Unknown Event",
            ),
            font=("Arial", 14, "bold"),
        ).pack(
            anchor="w",
        )

        ttk.Label(
            main_frame,
            text=f"Market: {market.get('market_name', 'Unknown Market')}",
            font=("Arial", 11),
        ).pack(
            anchor="w",
            pady=(0, 20),
        )

        # -------------------------
        # Add selection form
        # -------------------------

        entry_frame = ttk.Frame(
            main_frame
        )
        entry_frame.pack(
            fill="x",
            pady=(0, 15),
        )

        name_var = tk.StringVar()
        price_var = tk.StringVar()

        ttk.Label(
            entry_frame,
            text="Selection",
        ).grid(
            row=0,
            column=0,
            sticky="w",
        )

        ttk.Label(
            entry_frame,
            text="Price",
        ).grid(
            row=0,
            column=1,
            sticky="w",
            padx=(10, 0),
        )

        name_entry = ttk.Entry(
            entry_frame,
            textvariable=name_var,
            width=35,
        )
        name_entry.grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(5, 0),
        )

        price_entry = ttk.Entry(
            entry_frame,
            textvariable=price_var,
            width=15,
        )
        price_entry.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(10, 0),
            pady=(5, 0),
        )

        entry_frame.columnconfigure(
            0,
            weight=1,
        )

        # -------------------------
        # Existing selections
        # -------------------------

        selections_frame = ttk.LabelFrame(
            main_frame,
            text="Selections Added",
            padding=10,
        )
        selections_frame.pack(
            fill="both",
            expand=True,
            pady=(0, 15),
        )

        selection_list = tk.Listbox(
            selections_frame,
            height=12,
        )
        selection_list.pack(
            fill="both",
            expand=True,
        )

        def refresh_selection_list():
            selection_list.delete(
                0,
                "end",
            )

            for selection in market.get(
                "selections",
                [],
            ):
                selection_list.insert(
                    "end",
                    (
                        f"{selection.get('name', 'Unnamed')} "
                        f"— {selection.get('price', '')}"
                    ),
                )

        def add_new_selection():
            selection_name = (
                name_var.get().strip()
            )

            price = (
                price_var.get().strip()
            )

            if not selection_name:
                messagebox.showwarning(
                    "Add Selection",
                    "Selection name cannot be blank.",
                    parent=popup,
                )
                return

            if not price:
                messagebox.showwarning(
                    "Add Selection",
                    "Please enter a starting price.",
                    parent=popup,
                )
                return

            try:
                if "/" not in price:
                    raise ValueError

                numerator, denominator = price.split("/", 1)

                numerator = int(numerator.strip())
                denominator = int(denominator.strip())

                if denominator <= 0:
                    raise ValueError

                parsed_price = [
                    numerator,
                    denominator,
                ]

            except ValueError:
                messagebox.showwarning(
                    "Add Selection",
                    "Price must be entered as fractional odds, for example 3/1, 10/11 or 4/7.",
                    parent=popup,
                )
                return

            try:
                add_selection(
                    market,
                    selection_name,
                    parsed_price,
                )
            except Exception as error:
                messagebox.showerror(
                    "Add Selection",
                    str(error),
                    parent=popup,
                )
                return

            market["selections"].sort(
                key=lambda selection: probability(
                    selection["price"][0],
                    selection["price"][1],
                ),
                reverse=True,
            )

            touch_event(event)
            save_platform(self.platform)

            name_var.set("")
            price_var.set("")

            refresh_selection_list()

            name_entry.focus_set()

        ttk.Button(
            entry_frame,
            text="Add Selection",
            command=add_new_selection,
        ).grid(
            row=1,
            column=2,
            padx=(10, 0),
            pady=(5, 0),
        )

        # Pressing Enter adds the runner
        popup.bind(
            "<Return>",
            lambda event_key: add_new_selection(),
        )

        # -------------------------
        # Finish
        # -------------------------

        bottom_frame = ttk.Frame(
            main_frame
        )
        bottom_frame.pack(
            fill="x",
        )

        ttk.Button(
            bottom_frame,
            text="Finish",
            command=lambda: (
                popup.destroy(),
                self.show_import_centre(),
            ),
        ).pack(
            side="right",
        )

        refresh_selection_list()
        name_entry.focus_set()

    def choose_excel_import_file(self):
        file_path = filedialog.askopenfilename(
            title="Choose Excel Pricing File",
            filetypes=[
                (
                    "Excel workbooks",
                    "*.xlsx *.xlsm",
                ),
                (
                    "All files",
                    "*.*",
                ),
            ],
        )

        if not file_path:
            return

        self.import_file_path.set(file_path)

        try:
            preview = preview_excel_import(file_path)
        except Exception as error:
            messagebox.showerror(
                "Import Centre",
                f"Could not read the Excel file:\n\n{error}",
            )
            return

        self.current_import_preview = preview

        for widget in self.import_preview_frame.winfo_children():
            widget.destroy()

        event_name = preview.get("event") or "Not found"
        market_name = preview.get("market") or "Not found"
        category = preview.get("category") or "Not found"
        event_class = preview.get("class") or "Not found"
        event_type = preview.get("type") or "Not found"
        event_date = preview.get("date") or "Not found"
        event_time = preview.get("time") or "Not found"
        selection_count = len(preview.get("selections", []))

        display_date = event_date
        display_time = event_time

        if hasattr(display_date, "strftime"):
            display_date = display_date.strftime("%d/%m/%Y")

        if hasattr(display_time, "strftime"):
            display_time = display_time.strftime("%H:%M")


        preview_text = (
            f"Event: {event_name}\n"
            f"Market: {market_name}\n"
            f"Category: {category}\n"
            f"Class: {event_class}\n"
            f"Type: {event_type}\n"
            f"Date: {display_date}\n"
            f"Time: {display_time}\n"
            f"Selections found: {selection_count}"
        )

        ttk.Label(
            self.import_preview_frame,
            text=preview_text,
            justify="left",
        ).pack(
            anchor="w",
            padx=15,
            pady=15,
        )

    def import_excel_event(self):
        preview = getattr(self, "current_import_preview", None)

        if not preview:
            messagebox.showwarning(
                "Import Centre",
                "Choose and preview an Excel file first.",
            )
            return

        # Look for an existing active event with the same name.
        existing_event = next(
            (
                existing
                for existing in self.platform
                if existing.get(
                    "event_name",
                    "",
                ).strip().lower()
                == preview["event"].strip().lower()
                and not existing.get(
                    "archived",
                    False,
                )
            ),
            None,
        )

        new_event_created = False

        if existing_event:
            event = existing_event

        else:
            event = create_event(
                preview["category"],
                preview["class"],
                preview["type"],
                preview["event"],
            )

            event_date = preview.get("date")
            event_time = preview.get("time")

            if hasattr(event_date, "strftime"):
                event_date = event_date.strftime("%d/%m/%Y")

            if hasattr(event_time, "strftime"):
                event_time = event_time.strftime("%H:%M")

            event["start_time"] = f"{event_date} {event_time}"
            event["status"] = "Draft"
            event["published"] = False
            event["displayed"] = False

            self.platform.append(event)
            new_event_created = True


        # Check whether this market already exists in the event.
        existing_market = next(
            (
                existing
                for existing in event.get(
                    "markets",
                    [],
                )
                if existing.get(
                    "name",
                    "",
                ).strip().lower()
                == preview["market"].strip().lower()
            ),
            None,
        )

        if existing_market:
            messagebox.showwarning(
                "Import Centre",
                (
                    f"The market '{preview['market']}' already exists "
                    f"in {preview['event']}.\n\n"
                    "Nothing has been imported."
                ),
            )

            # Remove the newly-created event if this somehow occurred
            # before any useful data was added.
            if new_event_created:
                self.platform.remove(event)

            return


        market = create_market(
            event,
            preview["market"],
        )

        market["status"] = "Suspended"
        market["published"] = False
        market["displayed"] = False

        for runner in preview["selections"]:
            price_text = str(runner["price"]).strip()

            try:
                numerator, denominator = price_text.split("/", 1)

                parsed_price = [
                    int(numerator.strip()),
                    int(denominator.strip()),
                ]

            except (ValueError, AttributeError):
                messagebox.showwarning(
                    "Import Centre",
                    f"Invalid price for {runner['name']}: {price_text}",
                )
                return

            selection = add_selection(
                market,
                runner["name"],
                parsed_price,
            )

            selection["active"] = False
            selection["displayed"] = False


        # Existing events need a new version/change ID because
        # we have added a new market to them.
        if not new_event_created:
            touch_event(event)

        save_platform(self.platform)

        messagebox.showinfo(
            "Import Complete",
            (
                f"{preview['event']} imported successfully.\n\n"
                f"Market: {preview['market']}\n"
                f"Selections: {len(preview['selections'])}"
            ),
        )

        self.show_trading()

    def search_dashboard(self):
        search_term = self.search_entry.get().strip().lower()

        if not search_term:
            messagebox.showinfo(
                "Search",
                "Enter an event, market or selection name."
            )
            return

        matches = []

        for event in self.platform:
            event_name = event.get(
                "event_name",
                "Unnamed Event"
            )

            if search_term in event_name.lower():
                matches.append(
                    {
                        "type": "event",
                        "event": event,
                        "label": event_name,
                    }
                )

            for market in event.get("markets", []):
                market_name = market.get(
                    "name",
                    "Unnamed Market"
                )

                if search_term in market_name.lower():
                    matches.append(
                        {
                            "type": "market",
                            "event": event,
                            "market": market,
                            "label": (
                                f"{event_name} > {market_name}"
                            ),
                        }
                    )

                for selection in market.get(
                    "selections",
                    [],
                ):
                    selection_name = selection.get(
                        "name",
                        "Unnamed Selection"
                    )

                    if search_term in selection_name.lower():
                        matches.append(
                            {
                                "type": "selection",
                                "event": event,
                                "market": market,
                                "selection": selection,
                                "label": (
                                    f"{event_name} > "
                                    f"{market_name} > "
                                    f"{selection_name}"
                                ),
                            }
                        )

        if not matches:
            messagebox.showinfo(
                "Search",
                f'No results found for "{search_term}".'
            )
            return

        if len(matches) == 1:
            self.open_search_result(matches[0])
            return

        self.show_search_results(
            search_term,
            matches,
        )

    def open_search_result(self, result):
        result_type = result["type"]
        event = result["event"]

        if result_type == "event":
            self.show_event_screen(event)
            return

        market = result["market"]
        self.show_market_screen(event, market)

    def show_search_results(
        self,
        search_term,
        matches,
    ):
        self.clear_content()

        ttk.Button(
            self.content,
            text="← Back to Dashboard",
            command=self.show_dashboard,
        ).pack(
            anchor="w",
            pady=(0, 15),
        )

        ttk.Label(
            self.content,
            text=f'Search results for "{search_term}"',
            font=("Arial", 22, "bold"),
        ).pack(
            anchor="w",
            pady=(0, 15),
        )

        for result in matches:
            ttk.Button(
                self.content,
                text=result["label"],
                command=lambda selected=result: (
                    self.open_search_result(selected)
                ),
            ).pack(
                fill="x",
                anchor="w",
                pady=4,
            )

    def open_event_placeholder(self, event_name):

        self.clear_content()

        ttk.Label(
            self.content,
            text=event_name,
            font=("Arial", 24, "bold")
        ).pack(anchor="w")

        ttk.Label(
            self.content,
            text="Event trading screen coming next.",
            font=("Arial", 12)
        ).pack(anchor="w", pady=10)

        ttk.Button(
            self.content,
            text="Back to Dashboard",
            command=self.show_dashboard
        ).pack(anchor="w", pady=20)

if __name__ == "__main__":

    platform = load_remote_platform()
    clients = load_clients()

    root = tk.Tk()

    app = OddsPlatformGUI(
        root,
        platform,
        clients
    )

    root.mainloop()