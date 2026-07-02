# Locking In FC — Career Mode

A FIFA/FC-style football **career mode management game** that runs in your browser. No install, no build step, no dependencies.

## Play

Open `index.html` in any browser. That's it.

## What's in the game

- **20 fictional clubs** in 4 tiers, each with a full generated squad (~440 players with pace/shooting/passing/dribbling/defending/physical, OVR, hidden potential, contracts, wages, market value)
- **Career loop**: day-by-day calendar, 38-round season, matchday with live text commentary, player ratings, league table, top scorers
- **Transfers**: summer + January windows, bid/counter-bid negotiation, wage demands, selling, releasing, contract renewals — and AI clubs trade among themselves
- **Seasons**: aging and growth toward potential, decline past 31, retirements, contract expiries, youth intake every summer, end-of-season awards (Golden Boot, Player of the Season, Best Young Player)
- **Manager career**: reputation, trophy cabinet, finances (gate receipts, wages, prize money), club-colored UI theming
- **Saves**: 3 manual slots + autosave after every match (localStorage)

## Files

| File | Purpose |
|---|---|
| `engine.js` | All game logic — pure JS, runs in browser and Node |
| `index.html` | The UI |
| `test.js` | Self-check: simulates two full seasons headlessly |

## Test

```
node test.js
```
