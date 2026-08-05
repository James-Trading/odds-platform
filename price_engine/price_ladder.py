from datetime import datetime

from state.app_state import mark_dirty

PRICE_LADDER = [
    [1, 500],
    [1, 250],
    [1, 100],
    [1, 50],
    [1, 33],
    [1, 25],
    [1, 20],
    [1, 16],
    [1, 14],
    [1, 12],
    [1, 10],
    [1, 9],
    [1, 8],
    [1, 7],
    [2, 13],
    [1, 6],
    [2, 11],
    [1, 5],
    [2, 9],
    [1, 4],
    [2, 7],
    [3, 10],
    [1, 3],
    [4, 11],
    [2, 5],
    [4, 9],
    [1, 2],
    [8, 15],
    [4, 7],
    [8, 13],
    [4, 6],
    [8, 11],
    [4, 5],
    [5, 6],
    [10, 11],
    [1, 1],
    [11, 10],
    [6, 5],
    [5, 4],
    [11, 8],
    [6, 4],
    [13, 8],
    [7, 4],
    [15, 8],
    [2, 1],
    [9, 4],
    [5, 2],
    [11, 4],
    [3, 1],
    [10, 3],
    [7, 2],
    [4, 1],
    [9, 2],
    [5, 1],
    [11, 2],
    [6, 1],
    [13, 2],
    [7, 1],
    [15, 2],
    [8, 1],
    [17, 2],
    [9, 1],
    [10, 1],
    [11, 1],
    [12, 1],
    [14, 1],
    [16, 1],
    [18, 1],
    [20, 1],
    [22, 1],
    [25, 1],
    [28, 1],
    [33, 1],
    [40, 1],
    [50, 1],
    [66, 1],
    [80, 1],
    [100, 1],
    [125, 1],
    [150, 1],
    [200, 1],
    [250, 1],
    [400, 1],
    [500, 1],
    [1000, 1],
    [2500, 1],
    [5000, 1],
]

def shorten_one_tick(selection):
    pass


def lengthen_one_tick(selection):
    pass


def set_price(selection, numerator, denominator):

    old_price = list(selection["price"])

    new_price = [
        numerator,
        denominator
    ]

    mark_dirty()

    if "price_history" not in selection:
        selection["price_history"] = []

    selection["price_history"].append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "old_price": old_price,
        "new_price": new_price
    })

    selection["price"] = new_price

def shorten_one_tick(selection):

    current = selection["price"]

    index = PRICE_LADDER.index(current)

    if index > 0:
        new_price = PRICE_LADDER[index - 1]

        set_price(
            selection,
            new_price[0],
            new_price[1]
        )


def lengthen_one_tick(selection):

    current = selection["price"]

    index = PRICE_LADDER.index(current)

    if index < len(PRICE_LADDER) - 1:
        new_price = PRICE_LADDER[index + 1]

        set_price(
            selection,
            new_price[0],
            new_price[1]
        )