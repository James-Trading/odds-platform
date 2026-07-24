import tkinter as tk
from tkinter import ttk, messagebox

from save_load import save_platform, load_platform
from client_save_load import load_clients

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
            command=lambda: self.show_page("Clients")
        ).pack(fill="x", pady=4)

        ttk.Button(
            self.sidebar,
            text="Import Centre",
            command=lambda: self.show_page("Import Centre")
        ).pack(fill="x", pady=4)

        ttk.Button(
            self.sidebar,
            text="Back Office",
            command=lambda: self.show_page("Back Office")
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

        self.search_entry.insert(
            0,
            "Search events, markets or selections..."
        )

        ttk.Button(
            top_bar,
            text="Search",
            command=self.search_placeholder
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

    def show_trading(self):

        self.clear_content()

        top_bar = ttk.Frame(self.content)
        top_bar.pack(fill="x", pady=(0, 20))

        ttk.Label(
            top_bar,
            text="Trading",
            font=("Arial", 24, "bold")
        ).pack(side="left")

        search_entry = ttk.Entry(
            top_bar,
            width=35,
            font=("Arial", 12)
        )

        search_entry.pack(side="right")

        search_entry.insert(
            0,
            "Search events..."
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

        for event in self.platform:

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

        ttk.Label(
            self.content,
            text="Markets",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", pady=(25, 10))

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

        table_frame = ttk.Frame(self.content)
        table_frame.pack(fill="both", expand=True)

        columns = (
            "selection", 
            "price",
            "probability",
            "shorten",
            "lengthen",
            "status"
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

            if market_is_suspended and is_pending:
                status_text = "Suspended / Pending"
            elif market_is_suspended:
                status_text = "Suspended"
            elif not selection_is_active and is_pending:
                status_text = "Suspended / Pending"
            elif not selection_is_active:
                status_text = "Suspended"
            elif is_pending:
                status_text = "Pending"
            else:
                status_text = "Active"

            if market_is_suspended or not selection_is_active:
                row_tag = "suspended"
            elif is_pending:
                row_tag = "pending"
            else:
                row_tag = ""

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

        for selection_index, selection in enumerate(
            market.get("selections", [])
        ):
            pending_key = (id(market), selection_index)

            if pending_key not in self.pending_prices:
                continue

            new_price = self.pending_prices[pending_key]

            set_price(
                selection,
                new_price[0],
                new_price[1],
            )

            del self.pending_prices[pending_key]
            changes_saved = True

        if changes_saved:
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
        if column_id not in ("#4", "#5", "#6"):
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

            save_platform(self.platform)

        except (TypeError, KeyError):
            messagebox.showerror(
                "Suspension failed",
                "The selection status could not be updated.",
            )
            return

        self.show_market_screen(event, market)

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


    def search_placeholder(self):

        search_term = self.search_entry.get()

        print(f"GUI search: {search_term}")


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

    platform = load_platform()
    clients = load_clients()

    root = tk.Tk()

    app = OddsPlatformGUI(
        root,
        platform,
        clients
    )

    root.mainloop()