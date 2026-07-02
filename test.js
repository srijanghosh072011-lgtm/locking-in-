// node test.js — sims two full seasons and asserts the world stays sane.
'use strict';
const assert = require('assert');
const E = require('./engine.js');

const G = E.newGame('Test Manager', 0);
assert.strictEqual(G.clubs.length, 20);
assert.strictEqual(G.fixtures.length, 380);
assert.strictEqual(G.clubs[0].players.length, 22);
for (const p of G.clubs.flatMap(c => c.players)) {
  assert(p.ovr >= 30 && p.ovr <= 99, 'ovr in range');
  assert(p.pot >= p.ovr, 'pot >= ovr');
  assert(p.value > 0 && p.wage >= 500, 'value/wage sane');
}

for (let season = 0; season < 2; season++) {
  let goals = 0, matches = 0, guard = 0;
  while (true) {
    assert(guard++ < 500, 'season should not run forever');
    const ev = E.advanceDay(G);
    if (ev === 'match') {
      const res = E.playRound(G);
      assert(res.user, 'user plays every round');
      goals += res.user.hg + res.user.ag;
      matches++;
    } else if (ev === 'seasonEnd') {
      const aw = E.endSeason(G);
      assert(aw.champion && aw.topScorer.goals > 0 && aw.userPos >= 1 && aw.userPos <= 20);
      break;
    }
  }
  assert.strictEqual(matches, 38);
  const avg = goals / matches;
  assert(avg > 1.2 && avg < 4.5, `goals/match plausible, got ${avg.toFixed(2)}`);
}

const tab = E.table(G);
assert.strictEqual(tab.reduce((s, r) => s + r.p, 0), 0, 'new season table is fresh');
assert.strictEqual(G.season, 3);
// save/load roundtrip
const G2 = JSON.parse(JSON.stringify(G));
assert.strictEqual(E.table(G2).length, 20);
console.log('all checks passed — season 3 ready, rep', G.rep);
