from bets.bet_creation import create_bet
from bets.bet_save_load import save_bets


def add_bet(
    bets,
    client,
    event,
    market,
    selection,
    stake,
    price,
    event_id,
    market_id,
    selection_id,
):

    bet = create_bet(
        client,
        event,
        market,
        selection,
        stake,
        price,
        event_id,
        market_id,
        selection_id,
    )

    bets.append(bet)

    save_bets(bets)

    print()
    print("✓ Bet added.")

def create_test_bet(bets):

    add_bet(
        bets,
        "William Hill",
        "Strictly Come Dancing 2026",
        "Winner",
        "Dani Dyer",
        100,
        [3, 1],
    )