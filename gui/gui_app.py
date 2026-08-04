import tkinter as tk
from tkinter import ttk, messagebox, filedialog

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
            command=self.show_import_centre,
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

    def toggle_event_publish(self, event):

        event["published"] = not event.get("published", False)

        save_platform(self.platform)

        self.show_event_screen(event)

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

            settle_market_results(
                self.platform,
                [],
                event,
                market,
                pending_results,
            )

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
            market["selections"].sort(
                key=lambda selection: probability(
                    selection["price"][0],
                    selection["price"][1],
                ),
                reverse=True,
            )

            touch_event(event)
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

            touch_event(event)
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

    def show_import_centre(self):
        self.clear_content()

        ttk.Label(
            self.content,
            text="Import Centre",
            font=("Arial", 20, "bold"),
        ).pack(
            anchor="w",
            pady=(0, 8),
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

        event = create_event(
            preview["category"],
            preview["class"],
            preview["type"],
            preview["event"],
        )

        event_date = preview.get("date")
        event_time = preview.get("time")

        if hasattr(event_date, "strftime"):
            event_date = event_date.strftime("%Y-%m-%d")

        if hasattr(event_time, "strftime"):
            event_time = event_time.strftime("%H:%M")

        event["start_time"] = f"{event_date} {event_time}"
        event["status"] = "Draft"
        event["published"] = False
        event["displayed"] = False

        market = create_market(
            event,
            preview["market"],
        )

        market["status"] = "Suspended"
        market["published"] = False
        market["displayed"] = False

        for runner in preview["selections"]:
            selection = add_selection(
                market,
                runner["name"],
                str(runner["price"]),
            )

            selection["active"] = False
            selection["displayed"] = False

        self.platform.append(event)
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