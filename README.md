# Locking In FC — Career Mode

A FIFA/FC-style football **career mode management game** with **real clubs, real players, real faces and crests**, running entirely in your browser. No install, no build step, no dependencies.

Rosters are EA FC 26 **plus the real summer 2026 transfers** (Konaté, Bernardo Silva, Cucurella and Dumfries to Real Madrid; Gordon to Barcelona; Robertson, van Hecke, Senesi and Dúbravka to Spurs; Anderson to Man City; Jacquet to Liverpool).

Player photos and club crests load from sofifa's public CDN at runtime (with clean silhouette/shield fallbacks when offline).

## Play

Open `index.html` in any browser. That's it.

## The world

**7,893 real players** across **282 real clubs** in **14 real leagues**, with real EA FC 26 ratings (OVR, potential, pace/shooting/passing/dribbling/defending/physical, market values, wages, contract lengths):

| Manageable | Second divisions (with promotion/relegation) | Buy/sell markets |
|---|---|---|
| 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League | 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Championship | 🇸🇦 Saudi Pro League |
| 🇪🇸 La Liga | 🇪🇸 La Liga 2 | 🇺🇸 MLS |
| 🇩🇪 Bundesliga | 🇩🇪 2. Bundesliga | 🇹🇷 Süper Lig |
| 🇮🇹 Serie A | 🇮🇹 Serie B | |
| 🇫🇷 Ligue 1 | 🇫🇷 Ligue 2 | |
| 🇵🇹 Primeira Liga | *(no D2 in dataset — closed league)* | |

All 11 European leagues are manageable (yes, you can start in the Championship). The Saudi league, MLS, and Süper Lig play their own seasons, buy your stars with silly money, and sell to you.

## Competitions

- **Domestic leagues** — full double round-robin seasons, promotion & relegation (bottom 3 ↔ top 3; nobody drops out of D2)
- **Domestic cups** — FA Cup, Copa del Rey, DFB-Pokal, Coppa Italia, Coupe de France, Taça de Portugal (32-team knockouts, penalties on draws)
- **Champions League & Europa League** — 8 groups of 4, then knockout rounds to a final; qualification from real league finishes each season
- End-of-season awards, per-league champions, top scorer charts

## Career features

- Day-by-day calendar; matchdays with live text commentary and player ratings
- Summer + January transfer windows: bid/counter negotiation, wage demands, selling, releasing, renewals — and ~hundreds of AI transfers per window happening around you
- AI clubs bid for **your** players mid-window (Saudi clubs offer 1.3–2× value; hard to say no)
- Player growth toward real potential, decline past 31, retirement, contract expiries, youth academy intake every summer
- Finances: broadcast money by league, matchday gates, prize money, real wage bills
- Manager reputation and trophy cabinet across unlimited seasons
- 3 save slots + autosave after every match (localStorage)

## Files

| File | Purpose |
|---|---|
| `data.js` | Generated dataset: 282 clubs / 7,893 players (EA FC 26 + 2026 window patches) |
| `engine.js` | All game logic — pure JS, runs in browser and Node |
| `index.html` | The UI, themed in your club's colors |
| `test.js` | Self-check: simulates two full world seasons headlessly |
| `tools/build-data.js` | Rebuilds `data.js` from a sofifa CSV dump |

## Test

```
node test.js
```

## Rebuilding the data

`data.js` is generated from a public EA FC 26 player dump (sofifa export, [FC26_Dataset.csv](https://github.com/Peritosh/FC_26_Analysis_Report)):

```
node tools/build-data.js FC26_Dataset.csv
```

To upgrade to FC 27 data when a public dump appears, point the script at the new CSV — the column format is the standard sofifa export.
