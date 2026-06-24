from event_creation_functions import (
    create_platform_event,
    create_platform_market,
    create_platform_selection,
    create_template_event
)

from save_load import save_platform
from display_functions import display_platform


def handle_create_event(platform):

    create_platform_event(platform)

    save_platform(platform)

    display_platform(platform)


def handle_create_market(platform):

    create_platform_market(platform)

    save_platform(platform)

    display_platform(platform)


def handle_create_selection(platform):

    create_platform_selection(platform)

    save_platform(platform)

    display_platform(platform)


def handle_create_template_event(platform):

    create_template_event(platform)

    save_platform(platform)

    display_platform(platform)