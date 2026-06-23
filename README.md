# Odds Platform

## Purpose

A Python trading platform inspired by the William Hill trading platform and OpenBet hierarchy.

The aim is to build a sportsbook engine first, then add interfaces later.

---

## Structure

Platform
    Event
        Market
            Selection

Example:

Platform
└── Strictly Come Dancing 2026
      ├── Outright
      │     ├── Dani Dyer
      │     ├── Delta Goodrem
      │     └── Lacey Turner
      │
      └── Top 3 Finish

---

## Files

### event_app.py

Main program.

### event_functions.py

Functions for creating events, markets and selections.

### market_functions.py

Functions for market-level actions.

### platform_functions.py

Functions that operate from platform level.

Examples:

- change_platform_price()
- suspend_platform_selection()
- suspend_platform_event()
- settle_platform_market()
- void_platform_market()

### display_functions.py

Functions for displaying platform, events and markets.

### search_functions.py

Functions for finding:

- events
- markets
- selections

### pricing.py

Probability calculations.

### templates.py

Market templates.

### menu.py

User menu.

---

## Current Features

✓ Multiple events

✓ Multiple markets

✓ Multiple selections

✓ Active / Suspended

✓ Displayed / Hidden

✓ Market status

✓ Event suspension

✓ Selection suspension

✓ Price changes

✓ Market settlement

✓ Market voiding

✓ Book percentage

✓ Menu driven interface

---

## Future Ideas

- Looping menu
- README updates
- Git/GitHub
- CSV import
- Trading screen
- OpenBet view
- Search screen
- GUI
- Each-way markets
- Win/place books
- Resulting
- Bet settlement
- Customer bets
- Liabilities
- Trading alerts

---

## Philosophy

Build the engine first.

The interface sits on top of the engine.

The project is based on the concepts used by William Hill and OpenBet.
.
