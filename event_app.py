from event_functions import create_event, create_market, add_selection
from pricing import probability
from market_functions import change_event_price
from display_functions import (
    display_platform,
    display_event_names,
    display_market_names,
    display_selection_names,
    choose_event,
    choose_market,
    choose_selection
)
from market_functions import suspend_market, open_market
from market_functions import hide_selection
from search_functions import find_event
from platform_functions import change_platform_price
from platform_functions import change_platform_price, suspend_platform_selection
from platform_functions import (
    change_platform_price,
    suspend_platform_selection,
    suspend_platform_event
)
from platform_functions import (
    change_platform_price,
    suspend_platform_selection,
    suspend_platform_event,
    settle_platform_market,
    void_platform_market
)
from templates import create_outright_market
from menu import show_menu
from save_load import save_platform, load_platform

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

        event = choose_event(platform)
  
        event_name = event["event_name"]

        if event:

            market = choose_market(event)

            market_name = market["name"]
            selection = choose_selection(market)

            selection_name = selection["name"]

            top = int(input("Numerator: "))
            bottom = int(input("Denominator: "))

            change_platform_price(
            platform,
            event_name,
            market_name,
            selection_name,
            (top, bottom)
        )
        save_platform(platform)

        display_platform(platform)

    elif choice == "3":

        event = choose_event(platform)

        market = choose_market(event)

        selection = choose_selection(market)

        selection_name = selection["name"]

        suspend_platform_selection(
        platform,
        event["event_name"],
        market["name"],
        selection_name
        )

        display_platform(platform)

    elif choice == "4":


        event = choose_event(platform)

        suspend_platform_event(
        platform,
        event["event_name"]
        )

        display_platform(platform)

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

        display_platform(platform)

    elif choice == "6":

        event = choose_event(platform)

        market = choose_market(event)

        void_platform_market(
        platform,
        event["event_name"],
        market["name"]
        )

        display_platform(platform)

    elif choice == "7":
        print("Goodbye")
        running = False