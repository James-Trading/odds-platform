from event_functions import create_event
from templates import create_eurovision_template, create_strictly_template

def create_template_event(platform):

    print()
    print("1 Eurovision")
    print("2 Strictly")

    choice = input("Template: ")

    event_name = input("Event Name: ")

    if choice == "1":

        event = create_eurovision_template(event_name)

        platform.append(event)

        print("Template event created.")

    elif choice == "2":

        event = create_strictly_template(event_name)

        platform.append(event)

        print("Template event created.")


def create_platform_event(platform):

    category = input("Category: ")

    event_class = input("Class: ")

    event_type = input("Type: ")

    event_name = input("Event Name: ")

    event = create_event(
        category,
        event_class,
        event_type,
        event_name
    )

    platform.append(event)

    print("Event created.")

def create_platform_market(platform):

    from display_functions import choose_event
    from event_functions import create_market

    event = choose_event(platform)

    market_name = input("Market Name: ")

    create_market(
        event,
        market_name
    )

    print("Market created.")

def create_platform_selection(platform):

    from display_functions import (
        choose_event,
        choose_market
    )

    from event_functions import add_selection

    event = choose_event(platform)

    market = choose_market(event)

    selection_name = input("Selection Name: ")

    numerator = int(input("Numerator: "))

    denominator = int(input("Denominator: "))

    add_selection(
        market,
        selection_name,
        (numerator, denominator)
    )

    print("Selection created.")