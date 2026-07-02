// node test.js — sims two full seasons of the real-data world and asserts sanity.
'use strict';
const assert = require('assert');
const E = require('./engine.js');
const D = require('./data.js');

const liv = D.clubs.findIndex(c => c.n === 'Liverpool');
assert(liv >= 0, 'Liverpool exists');
const G = E.newGame('Test Manager', liv);

assert.strictEqual(G.clubs.length, 282);
assert(G.clubs.flatMap(c => c.players).length > 7500, 'full player pool loaded');
const sizes0 = D.leagues.map((L, li) => E.leagueClubs(G, li).length);
assert.strictEqual(G.fixtures.filter(f => f.c === 'L0').length, 380, 'PL has 380 matches');
assert.strictEqual(G.fixtures.filter(f => f.c === 'L6').length, 552, 'Championship has 552 matches');
assert.strictEqual(G.fixtures.filter(f => f.c === 'UCLg').length, 96, 'UCL groups: 8x12 matches');
assert(G.knock.C0.alive.length === 32, 'FA Cup has 32 entrants');
const mbappe = G.clubs.flatMap(c => c.players).find(p => p.name === 'K. Mbappé');
assert(mbappe && mbappe.ovr === 91, 'real ratings loaded');

for (let season = 0; season < 2; season++) {
  let goals = 0, matches = 0, guard = 0;
  const t0 = Date.now();
  while (true) {
    assert(guard++ < 500, 'season should not run forever');
    const ev = E.advanceDay(G);
    if (ev === 'match') {
      const res = E.playDay(G);
      assert(res.user, 'user plays when told match day');
      goals += res.user.hg + res.user.ag;
      matches++;
    } else if (ev === 'offer') {
      if (Math.random() < 0.2) E.acceptOffer(G); else G.pendingOffer = null;
    } else if (ev === 'seasonEnd') {
      assert(G.knock.UCL.alive.length === 1, 'UCL has a winner');
      assert(G.knock.UEL.alive.length === 1, 'UEL has a winner');
      for (const li of G.cupCountries) assert(G.knock['C' + li].alive.length === 1, 'cup winner: ' + li);
      const sum = E.endSeason(G);
      assert(sum.champions.length === 9 && sum.proms.length === 5 && sum.awards.topScorer.goals > 0);
      break;
    }
  }
  assert(matches >= 38, `user plays league + cups, got ${matches}`);
  const avg = goals / matches;
  assert(avg > 1.2 && avg < 4.5, `goals/match plausible, got ${avg.toFixed(2)}`);
  // promotion/relegation kept every league at its correct size
  D.leagues.forEach((L, li) => assert.strictEqual(E.leagueClubs(G, li).length, sizes0[li], 'league size stable: ' + L.name));
  console.log(`season ${season + 1}: ${matches} user matches, ${avg.toFixed(2)} goals/match, ${Date.now() - t0}ms`);
}

assert.strictEqual(G.season, 3);
const json = JSON.stringify(G);
const G2 = JSON.parse(json);
assert.strictEqual(E.table(G2, 'L0').length, 20, 'save/load roundtrip');
console.log(`all checks passed — save size ${(json.length / 1e6).toFixed(2)}M chars, rep ${G.rep}, trophies: ${G.trophies.length}`);
