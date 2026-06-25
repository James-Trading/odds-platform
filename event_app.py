from event_functions import create_event, create_market, add_selection
from audit_functions import add_audit_log, display_audit_log
from pricing import probability
from pricing_actions import handle_price_change
from display_functions import (
    display_platform,
    display_event,
    display_event_names,
    display_market_names,
    display_selection_names,
    choose_event,
    choose_market,
    choose_selection
)
from search_display_functions import search_platform
from event_creation_functions import (
    create_platform_event,
    create_platform_market,
    create_platform_selection,
    create_template_event
)
from market_functions import (
    change_event_price,
    suspend_market,
    open_market,
    unsuspend_market,
    hide_selection
)

from search_functions import find_event

from actions.creation_actions import (
    handle_create_event,
    handle_create_market,
    handle_create_selection,
    handle_create_template_event
)

from actions.deletion_actions import (
    handle_delete_selection,
    handle_delete_market,
    handle_delete_event
)

from actions.suspension_actions import (
    handle_suspend_selection,
    handle_suspend_event,
    handle_suspend_market,
    handle_unsuspend_selection,
    handle_unsuspend_market,
    handle_unsuspend_event
)

from platform_functions import (
    change_platform_price,
    suspend_platform_selection,
    suspend_platform_event,
    settle_platform_market,
    suspend_platform_market,
    void_platform_market,
    unsuspend_platform_selection,
    unsuspend_platform_market,
    unsuspend_platform_event
)
from templates import create_outright_market
from menu import show_menu
from save_load import save_platform, load_platform
from delete_functions import delete_selection, delete_market, delete_event

from client_save_load import load_clients
from actions.client_actions import (
    handle_add_client,
    handle_view_clients,
    handle_book_event,
    handle_view_client,
    handle_unbook_event
)

from submenus import show_main_menu

clients = load_clients()

platform = load_platform()

if platform == []:

    event = create_event(
    "SPECIALS",
    "TV Specials",
    "Strictly Come Dancing",
    "Strictly Come Dancing 2026"
    )

    outright_market = create_market(event, "Outright")

    top3_market = create_market(event, "Top 3 Finish")

    add_selection(outright_market, "Dani Dyer", (4, 1))
    add_selection(outright_market, "Delta Goodrem", (5, 1))
    add_selection(outright_market, "Lacey Turner", (7, 1))

    add_selection(top3_market, "Dani Dyer", (1, 2))
    add_selection(top3_market, "Delta Goodrem", (4, 5))
    add_selection(top3_market, "Lacey Turner", (6, 4))

    platform.append(event)

    eurovision = create_event(
    "SPECIALS",
    "Music Specials",
    "Eurovision",
    "Eurovision 2027"
    )

    runners = [
    ("Sweden", (4,1)),
    ("Italy", (6,1)),
    ("Ukraine", (8,1))
    ]

    eurovision_winner = create_outright_market(
    eurovision,
    "Winner",
    runners
    )

    platform.append(eurovision)

    change_platform_price(
    platform,
    "Eurovision 2027",
    "Winner",
    "Sweden",
    (3,1)
    )

# suspend_platform_selection(
#     platform,
#     "Eurovision 2027",
#     "Winner",
#     "Italy"
# )

# suspend_platform_event(
#     platform,
#     "Strictly Come Dancing 2026"
# )

# settle_platform_market(
#     platform,
#     "Eurovision 2027",
#     "Winner",
#     "Sweden"
# )

# void_platform_market(
#     platform,
#     "Eurovision 2027",
#     "Winner"
# )

#display_platform(platform)

running = True

while running:

    choice = show_menu()

    if choice == "1":
        
        display_platform(platform)

    elif choice == "2":

        handle_price_change(platform)

    elif choice == "3":
        handle_suspend_selection(platform)

    elif choice == "4":
        handle_suspend_event(platform)

    elif choice == "5":

        event = choose_event(platform)

        market = choose_market(event)

        winner = choose_selection(market)

        settle_platform_market(
        platform,
        event["event_name"],
        market["name"],
        winner["name"]
        )

        add_audit_log(
            f'{market["name"]} settled - Winner: {winner["name"]}'
        )

        save_platform(platform)
        display_platform(platform)

    elif choice == "6":

        event = choose_event(platform)

        market = choose_market(event)

        void_platform_market(
        platform,
        event["event_name"],
        market["name"]
        )

        add_audit_log(
            f'{market["name"]} voided'
        )

        save_platform(platform)
        display_platform(platform)

    elif choice == "7":
        handle_suspend_market(platform)

    elif choice == "8":
        handle_unsuspend_selection(platform)

    elif choice == "9":
        handle_unsuspend_market(platform)

    elif choice == "10":
        handle_unsuspend_event(platform)

    elif choice == "11":

        search_term = input("Search: ")

        search_platform(
        platform,
        search_term
        )

    elif choice == "12":

        handle_create_event(platform)

    elif choice == "13":

        handle_create_market(platform)

    elif choice == "14":

        handle_create_selection(platform)

    elif choice == "15":

        handle_create_template_event(platform)


    elif choice == "16":

        display_audit_log()

    elif choice == "17":

        handle_delete_selection(platform)

    elif choice == "18":

        handle_delete_market(platform)

    elif choice == "19":

        handle_delete_event(platform)

    elif choice == "20":

        handle_add_client(clients)


    elif choice == "21":

        handle_view_clients(clients)

    elif choice == "22":

        event = choose_event(platform)

        display_event(event)

    elif choice == "23":

        handle_book_event(
            clients,
            platform
        )

    elif choice == "24":

        handle_view_client(clients)

    elif choice == "25":

        handle_unbook_event(clients)

    elif choice == "26":

        print("Goodbye")

        running = False