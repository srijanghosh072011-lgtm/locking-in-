// engine.js — pure game logic. Runs in browser (globals) and node (module.exports).
'use strict';

const DAY = 86400000;
const R = n => Math.floor(Math.random() * n);
const rnd = (a, b) => a + Math.random() * (b - a);
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const pick = a => a[R(a.length)];

// ---------- names & nations ----------
const NAMES = {
  England: { f: ['Jack', 'Harry', 'Ollie', 'George', 'Lewis', 'Callum', 'Mason', 'Reece', 'Kyle', 'Aaron', 'Ben', 'Joe'], l: ['Walker', 'Hughes', 'Baker', 'Turner', 'Clark', 'Ward', 'Foster', 'Gibson', 'Hall', 'Dawson', 'Reid', 'Cole'] },
  Spain: { f: ['Pablo', 'Sergio', 'Iker', 'Dani', 'Alvaro', 'Marco', 'Hugo', 'Adrian', 'Raul', 'Javi', 'Nico', 'Pedro'], l: ['Garcia', 'Torres', 'Navarro', 'Moreno', 'Vazquez', 'Serrano', 'Ortega', 'Ramos', 'Gil', 'Castro', 'Rubio', 'Molina'] },
  Brazil: { f: ['Gabriel', 'Lucas', 'Matheus', 'Vinicius', 'Thiago', 'Rafael', 'Caio', 'Joao', 'Pedro', 'Eduardo', 'Felipe', 'Igor'], l: ['Silva', 'Santos', 'Oliveira', 'Souza', 'Costa', 'Pereira', 'Almeida', 'Ferreira', 'Ribeiro', 'Barbosa', 'Rocha', 'Dias'] },
  France: { f: ['Kylian', 'Antoine', 'Theo', 'Hugo', 'Lucas', 'Jules', 'Enzo', 'Mathis', 'Noah', 'Leo', 'Rayan', 'Malo'], l: ['Martin', 'Bernard', 'Dubois', 'Moreau', 'Laurent', 'Girard', 'Lambert', 'Fontaine', 'Rousseau', 'Mercier', 'Blanc', 'Renard'] },
  Germany: { f: ['Leon', 'Finn', 'Jonas', 'Lukas', 'Felix', 'Niklas', 'Tim', 'Moritz', 'Jan', 'Erik', 'Til', 'Kai'], l: ['Muller', 'Schmidt', 'Weber', 'Wagner', 'Becker', 'Hoffmann', 'Schulz', 'Koch', 'Richter', 'Klein', 'Wolf', 'Braun'] },
  Nigeria: { f: ['Chidi', 'Emeka', 'Kelechi', 'Obinna', 'Sola', 'Tunde', 'Ifeanyi', 'Uche', 'Femi', 'Sam', 'David', 'Victor'], l: ['Okafor', 'Adeyemi', 'Eze', 'Okonkwo', 'Balogun', 'Ibe', 'Nwosu', 'Adebayo', 'Chukwu', 'Obi', 'Musa', 'Lawal'] },
  Argentina: { f: ['Lionel', 'Julian', 'Lautaro', 'Emiliano', 'Nicolas', 'Rodrigo', 'Facundo', 'Thiago', 'Franco', 'Mateo', 'Bruno', 'Tomas'], l: ['Fernandez', 'Rodriguez', 'Gonzalez', 'Lopez', 'Martinez', 'Diaz', 'Alvarez', 'Romero', 'Sosa', 'Acosta', 'Medina', 'Rojas'] },
  Netherlands: { f: ['Daan', 'Sem', 'Luuk', 'Jesse', 'Thijs', 'Lars', 'Ruben', 'Bram', 'Sven', 'Koen', 'Milan', 'Teun'], l: ['de Jong', 'Bakker', 'Visser', 'Smit', 'Meijer', 'Mulder', 'Bos', 'Vos', 'Peters', 'Hendriks', 'Dekker', 'Brouwer'] },
};
const NATIONS = Object.keys(NAMES);

// ---------- clubs: [name, short, tier, color1, color2] ----------
const CLUB_DEFS = [
  ['Kingsport United', 'KSU', 1, '#c8102e', '#ffffff'],
  ['Blackmoor City', 'BMC', 1, '#6caddf', '#1c2c5b'],
  ['Redhaven FC', 'RHV', 1, '#d00027', '#ffd700'],
  ['Northgate Albion', 'NGA', 1, '#034694', '#ffffff'],
  ['Silverton Rovers', 'SLV', 2, '#7f8c9b', '#101820'],
  ['Eastcliff Town', 'ECT', 2, '#0057b8', '#ffd700'],
  ['Harborview FC', 'HBV', 2, '#00a398', '#132257'],
  ['Westbrook Wanderers', 'WBW', 2, '#fdb913', '#231f20'],
  ['Ironfield Athletic', 'IFA', 2, '#e03a3e', '#000000'],
  ['Oakhurst County', 'OAK', 3, '#046a38', '#f2a900'],
  ['Stonebridge FC', 'STB', 3, '#5e2750', '#9c9c9c'],
  ['Marston Villa', 'MSV', 3, '#95bfe5', '#670e36'],
  ['Greyfriars Rangers', 'GFR', 3, '#4a4f55', '#c00'],
  ['Lakemoor Town', 'LMT', 3, '#0f4d92', '#87ceeb'],
  ['Ashford City', 'AFC', 3, '#9b0000', '#f5f5f5'],
  ['Dunmere FC', 'DUN', 4, '#2f5233', '#e8e8e8'],
  ['Foxhill United', 'FOX', 4, '#e87722', '#1d1d1b'],
  ['Cindermill FC', 'CIN', 4, '#7a263a', '#a5acaf'],
  ['Wolverdale', 'WLV', 4, '#101820', '#fdb913'],
  ['Port Bramble', 'PBR', 4, '#00b2a9', '#003087'],
];
const TIER_BUDGET = [0, 80e6, 40e6, 18e6, 8e6];

// ---------- players ----------
// OVR weights per position: [pac, sho, pas, dri, def, phy]
const W = {
  GK: [.05, .10, .10, .05, .50, .20],
  DF: [.10, .05, .10, .05, .45, .25],
  MF: [.10, .15, .30, .20, .10, .15],
  AT: [.20, .35, .10, .20, .02, .13],
};
const SHAPE = { GK: [-15, -30, -8, -15, 6, 2], DF: [-2, -18, -5, -8, 6, 4], MF: [-3, -4, 6, 4, -8, -2], AT: [5, 6, -4, 4, -25, -1] };
const ATTRS = ['pac', 'sho', 'pas', 'dri', 'def', 'phy'];
let nextId = 1;

function calcOvr(p) {
  const w = W[p.pos];
  return Math.round(ATTRS.reduce((s, a, i) => s + p[a] * w[i], 0));
}
function calcValue(p) {
  if (p.ovr <= 55) return 100e3;
  const ageF = p.age <= 23 ? 1.3 : p.age <= 27 ? 1.1 : p.age <= 30 ? 1.0 : p.age <= 32 ? 0.6 : 0.3;
  const potF = 1 + (p.pot - p.ovr) * 0.02;
  return Math.max(100e3, Math.round(Math.pow(p.ovr - 55, 2.9) * 3000 * ageF * potF / 1e5) * 1e5);
}
function refresh(p) { p.ovr = calcOvr(p); p.value = calcValue(p); }

function genPlayer(tier, age, pos) {
  const nat = pick(NATIONS), n = NAMES[nat];
  age = age || 16 + Math.round((R(19) + R(19)) / 2);
  pos = pos || pick(['DF', 'DF', 'MF', 'MF', 'AT', 'AT', 'GK']);
  let base = 76 - (tier - 1) * 3 + rnd(-6, 6);
  if (Math.random() < 0.15) base += rnd(3, 8); // the odd star
  if (age < 21) base -= (21 - age) * 1.5;
  const p = { id: nextId++, name: pick(n.f) + ' ' + pick(n.l), nat, pos, age, fit: 100, injury: 0, apps: 0, sg: 0, sa: 0, listed: false };
  ATTRS.forEach((a, i) => p[a] = Math.round(clamp(base + SHAPE[pos][i] + rnd(-5, 5), 30, 99)));
  p.ovr = calcOvr(p);
  p.pot = clamp(p.ovr + Math.max(0, Math.round((27 - age) * rnd(0.5, 2.0))), p.ovr, 97);
  p.value = calcValue(p);
  p.wage = clamp(Math.round(p.value / 2500 / 100) * 100, 500, 400e3);
  p.years = 1 + R(4);
  return p;
}
function genSquad(tier) {
  const tmpl = ['GK', 'GK', 'DF', 'DF', 'DF', 'DF', 'DF', 'DF', 'DF', 'MF', 'MF', 'MF', 'MF', 'MF', 'MF', 'MF', 'AT', 'AT', 'AT', 'AT', 'AT', 'AT'];
  return tmpl.map(pos => genPlayer(tier, 0, pos));
}
const wageBill = c => c.players.reduce((s, p) => s + p.wage, 0);

// ---------- fixtures ----------
function roundRobin(ids) {
  const t = ids.slice(), n = t.length, rounds = [];
  for (let r = 0; r < n - 1; r++) {
    const rd = [];
    for (let i = 0; i < n / 2; i++) rd.push(r % 2 ? [t[n - 1 - i], t[i]] : [t[i], t[n - 1 - i]]);
    rounds.push(rd);
    t.splice(1, 0, t.pop());
  }
  return rounds;
}
function genFixtures(G) {
  const ids = G.clubs.map(c => c.id);
  const half = roundRobin(ids);
  const rounds = half.concat(half.map(rd => rd.map(([h, a]) => [a, h])));
  const start = Date.UTC(G.year, 7, 15); // Aug 15
  G.fixtures = [];
  rounds.forEach((rd, i) => rd.forEach(([h, a]) =>
    G.fixtures.push({ round: i + 1, t: start + i * 7 * DAY, h, a, hg: 0, ag: 0, played: false })));
}

// ---------- selection & strength ----------
const FORMATIONS = { '4-4-2': [4, 4, 2], '4-3-3': [4, 3, 3], '3-5-2': [3, 5, 2], '4-5-1': [4, 5, 1], '5-3-2': [5, 3, 2] };

function bestXI(c) {
  const need = { GK: 1 };
  const [d, m, a] = FORMATIONS[c.formation] || [4, 3, 3];
  need.DF = d; need.MF = m; need.AT = a;
  const fit = c.players.filter(p => !p.injury).sort((x, y) => y.ovr * y.fit - x.ovr * x.fit);
  const xi = [];
  for (const pos of ['GK', 'DF', 'MF', 'AT'])
    xi.push(...fit.filter(p => p.pos === pos && !xi.includes(p)).slice(0, need[pos]));
  // short in a position: pad with best remaining bodies (even injured, last resort)
  for (const p of fit.concat(c.players)) { if (xi.length >= 11) break; if (!xi.includes(p)) xi.push(p); }
  return xi;
}
function strength(c, xi, home) {
  const avgOvr = xi.reduce((s, p) => s + p.ovr, 0) / xi.length;
  const avgFit = xi.reduce((s, p) => s + p.fit, 0) / xi.length;
  return avgOvr + (c.morale - 70) / 10 + (avgFit - 85) / 10 + (home ? 2.5 : 0);
}

// ---------- match sim ----------
function simMatch(G, hc, ac, detailed) {
  const hXI = bestXI(hc), aXI = bestXI(ac);
  const ment = m => m === 'attacking' ? 2 : m === 'defensive' ? -2 : 0;
  const hs = strength(hc, hXI, true) + ment(hc.mentality);
  const as = strength(ac, aXI, false) + ment(ac.mentality);
  let hg = 0, ag = 0;
  const ev = [], scorers = { h: [], a: [] };
  const pickScorer = xi => { // attackers score most
    const pool = xi.flatMap(p => Array(p.pos === 'AT' ? 8 : p.pos === 'MF' ? 3 : p.pos === 'DF' ? 1 : 0).fill(p));
    return pool.length ? pick(pool) : xi[0];
  };
  for (let min = 1; min <= 90; min++) {
    for (const side of ['h', 'a']) {
      const my = side === 'h' ? hs : as, opp = side === 'h' ? as : hs;
      const c = side === 'h' ? hc : ac, xi = side === 'h' ? hXI : aXI;
      const r = clamp(my / opp, 0.6, 1.7);
      if (Math.random() < 0.13 * r * r) { // chance created
        const shooter = pickScorer(xi);
        if (Math.random() < 0.105 * r) {
          side === 'h' ? hg++ : ag++;
          shooter.sg++;
          scorers[side].push(shooter.name + " " + min + "'");
          let txt = `⚽ ${min}' GOAL! ${shooter.name} scores for ${c.short}!`;
          const mates = xi.filter(p => p !== shooter && p.pos !== 'GK');
          if (Math.random() < 0.65 && mates.length) { const a2 = pick(mates); a2.sa++; txt += ` (assist: ${a2.name})`; }
          ev.push({ min, txt, goal: side, score: `${hg}-${ag}` });
        } else if (detailed && Math.random() < 0.25) {
          ev.push({ min, txt: `${min}' ${shooter.name} (${c.short}) shoots — ${pick(['saved!', 'just wide!', 'off the bar!', 'blocked!'])}` });
        }
      }
    }
  }
  // post-match effects
  const ratings = [];
  for (const [c, xi, gf, ga] of [[hc, hXI, hg, ag], [ac, aXI, ag, hg]]) {
    const res = gf > ga ? 1 : gf < ga ? -1 : 0;
    c.morale = clamp(c.morale + res * 4 + (res === 0 ? 1 : 0), 30, 95);
    for (const p of xi) {
      p.apps++;
      p.fit = clamp(p.fit - rnd(8, 15), 20, 100);
      if (Math.random() < 0.035) { p.injury = 5 + R(25); ev.push({ min: 90, txt: `🩹 ${p.name} (${c.short}) picked up an injury (${p.injury} days).` }); }
      const g = scorers.h.concat(scorers.a).filter(s => s.startsWith(p.name + ' ')).length;
      ratings.push({ club: c.id, name: p.name, pos: p.pos, r: Math.round(clamp(6.4 + g * 1.2 + res * 0.4 + rnd(-0.7, 0.7), 4, 10) * 10) / 10 });
    }
  }
  return { hg, ag, ev, scorers, ratings };
}

function playRound(G) {
  const todays = G.fixtures.filter(f => f.t === G.time && !f.played);
  const out = { others: [], user: null };
  for (const f of todays) {
    const hc = G.clubs[f.h], ac = G.clubs[f.a];
    const isUser = f.h === G.userClub || f.a === G.userClub;
    const res = simMatch(G, hc, ac, isUser);
    f.hg = res.hg; f.ag = res.ag; f.played = true;
    if (isUser) {
      out.user = { f, ...res };
      const me = G.clubs[G.userClub];
      if (f.h === G.userClub) { // gate receipts
        const gate = (35000 - me.tier * 5000) * 30;
        me.budget += gate;
        G.tx.push({ t: G.time, txt: 'Matchday gate receipts', amt: gate });
      }
    } else out.others.push(f);
  }
  if (G.fixtures.every(f => f.played)) G.seasonOver = true;
  return out;
}

// ---------- table ----------
function table(G) {
  const rows = G.clubs.map(c => ({ id: c.id, name: c.name, short: c.short, p: 0, w: 0, d: 0, l: 0, gf: 0, ga: 0, pts: 0 }));
  for (const f of G.fixtures) {
    if (!f.played) continue;
    const h = rows[f.h], a = rows[f.a];
    h.p++; a.p++; h.gf += f.hg; h.ga += f.ag; a.gf += f.ag; a.ga += f.hg;
    if (f.hg > f.ag) { h.w++; h.pts += 3; a.l++; }
    else if (f.hg < f.ag) { a.w++; a.pts += 3; h.l++; }
    else { h.d++; a.d++; h.pts++; a.pts++; }
  }
  return rows.sort((x, y) => y.pts - x.pts || (y.gf - y.ga) - (x.gf - x.ga) || y.gf - x.gf);
}

// ---------- calendar ----------
const windowOpen = G => [0, 5, 6, 7].includes(new Date(G.time).getUTCMonth()); // Jan + Jun–Aug

function advanceDay(G) {
  G.time += DAY;
  const d = new Date(G.time);
  for (const c of G.clubs) for (const p of c.players) {
    if (p.injury > 0) p.injury--;
    p.fit = clamp(p.fit + 3, 20, 100);
  }
  G.clubs[G.userClub].budget -= wageBill(G.clubs[G.userClub]) / 7;
  if ((d.getUTCMonth() === 8 || d.getUTCMonth() === 1) && d.getUTCDate() === 1) {
    aiTransfers(G);
    news(G, '🚪 The transfer window has closed.');
  }
  if (G.seasonOver) return 'seasonEnd';
  if (G.fixtures.some(f => f.t === G.time && !f.played)) return 'match';
  return null;
}

function news(G, txt) { G.news.unshift({ t: G.time, txt }); G.news.length = Math.min(G.news.length, 60); }

// ---------- AI transfers (window close shuffle) ----------
function aiTransfers(G) {
  for (let i = 0; i < 20; i++) {
    const seller = pick(G.clubs), buyer = pick(G.clubs);
    if (seller.id === buyer.id || seller.id === G.userClub || buyer.id === G.userClub) continue;
    if (seller.players.length <= 18 || buyer.players.length >= 30) continue;
    const p = pick(seller.players);
    const fee = Math.round(p.value * rnd(0.9, 1.2));
    if (buyer.budget < fee || p.ovr > 72 + (5 - buyer.tier) * 6) continue;
    seller.players.splice(seller.players.indexOf(p), 1);
    buyer.players.push(p);
    buyer.budget -= fee; seller.budget += fee;
    if (p.ovr >= 74) news(G, `🔁 ${p.name} (${p.ovr}) joins ${buyer.name} from ${seller.name} for £${(fee / 1e6).toFixed(1)}M.`);
  }
}

// ---------- user transfer helpers ----------
function bid(G, p, seller, offer) {
  if (offer >= p.value * rnd(0.95, 1.25)) return { ok: true, fee: offer, wage: Math.round(p.wage * 1.25 / 100) * 100 };
  return { ok: false, counter: Math.round(p.value * 1.25 / 1e5) * 1e5 };
}
function signPlayer(G, p, seller, fee, wage) {
  const me = G.clubs[G.userClub];
  seller.players.splice(seller.players.indexOf(p), 1);
  me.players.push(p);
  me.budget -= fee; seller.budget += fee;
  p.wage = wage; p.years = 4; p.listed = false;
  G.tx.push({ t: G.time, txt: 'Signed ' + p.name, amt: -fee });
  news(G, `✍️ ${p.name} signs for ${me.name} for £${(fee / 1e6).toFixed(1)}M!`);
}
function sellPlayer(G, p) {
  const me = G.clubs[G.userClub];
  const buyer = pick(G.clubs.filter(c => c.id !== G.userClub));
  const fee = Math.round(p.value * rnd(0.8, 1.05) / 1e5) * 1e5;
  return { buyer, fee };
}
function completeSale(G, p, buyer, fee) {
  const me = G.clubs[G.userClub];
  me.players.splice(me.players.indexOf(p), 1);
  buyer.players.push(p);
  me.budget += fee;
  G.tx.push({ t: G.time, txt: 'Sold ' + p.name + ' to ' + buyer.name, amt: fee });
  news(G, `💰 ${p.name} sold to ${buyer.name} for £${(fee / 1e6).toFixed(1)}M.`);
}

// ---------- season end ----------
function developPlayer(p) {
  let d = 0;
  if (p.age <= 21) d = rnd(1, 4); else if (p.age <= 27) d = rnd(0, 2);
  else if (p.age >= 33) d = -rnd(2, 4); else if (p.age >= 31) d = -rnd(0, 2);
  if (d > 0) d = Math.min(d, p.pot - p.ovr);
  ATTRS.forEach(a => p[a] = Math.round(clamp(p[a] + d * rnd(0.6, 1.4), 30, 99)));
  refresh(p);
}

function endSeason(G) {
  const tab = table(G);
  const champion = G.clubs[tab[0].id];
  const userPos = tab.findIndex(r => r.id === G.userClub) + 1;
  const me = G.clubs[G.userClub];
  // prize money
  const prize = Math.round((21 - userPos) * 1.2e6);
  me.budget += prize;
  G.tx.push({ t: G.time, txt: `Season ${G.season} prize money (finished ${userPos})`, amt: prize });
  // awards
  const all = G.clubs.flatMap(c => c.players.map(p => ({ p, c })));
  const top = k => all.slice().sort((x, y) => k(y.p) - k(x.p))[0];
  const snap = x => ({ name: x.p.name, club: x.c.short, goals: x.p.sg, assists: x.p.sa, age: x.p.age });
  const awards = { // snapshot now: stats reset below
    userPos, prize, champion: champion.name,
    topScorer: snap(top(p => p.sg)), bestPlayer: snap(top(p => p.sg + p.sa)),
    bestYoung: snap(all.filter(x => x.p.age <= 21).sort((x, y) => y.p.ovr - x.p.ovr)[0]),
  };
  // manager rep + trophies
  G.rep = clamp(G.rep + (userPos <= 4 ? 5 : userPos <= 10 ? 2 : -3) + (userPos === 1 ? 10 : 0), 0, 100);
  if (userPos === 1) G.trophies.push(`League Champions — Season ${G.season} (${G.year}/${G.year + 1 - 2000})`);
  news(G, `🏆 ${champion.name} are champions! You finished ${userPos}.`);
  // aging, growth, retirement, contracts
  for (const c of G.clubs) {
    for (const p of c.players.slice()) {
      p.age++;
      developPlayer(p);
      p.sg = 0; p.sa = 0; p.apps = 0; p.fit = 100; p.injury = 0;
      p.years--;
      if (p.age >= 35 && Math.random() < (p.age - 34) * 0.35) {
        c.players.splice(c.players.indexOf(p), 1);
        if (c.id === G.userClub || p.ovr >= 80) news(G, `👋 ${p.name} (${p.age}) has retired.`);
        continue;
      }
      if (p.years <= 0) {
        if (c.id !== G.userClub && Math.random() < 0.8) { p.years = 1 + R(3); continue; } // AI auto-renews
        c.players.splice(c.players.indexOf(p), 1);
        if (c.id === G.userClub) news(G, `📄 ${p.name} left on a free — contract expired.`);
      }
    }
    // youth intake: 3 kids, quality tied to club tier (ponytail: no academy facility levels yet)
    for (let i = 0; i < 3; i++) c.players.push(genPlayer(c.tier, 16 + R(3)));
    c.budget = Math.max(c.budget, TIER_BUDGET[c.tier] * 0.6); // board tops up AI + floor for user
    c.morale = 70;
  }
  news(G, `🌱 Youth academy: 3 new prospects joined the academy.`);
  // next season
  G.season++; G.year++;
  G.seasonOver = false;
  G.time = Date.UTC(G.year, 6, 15); // Jul 15
  genFixtures(G);
  return awards;
}

// ---------- new game ----------
function newGame(managerName, clubId) {
  nextId = 1;
  const G = {
    season: 1, year: 2026, time: Date.UTC(2026, 6, 15),
    managerName, userClub: clubId, rep: 30, trophies: [],
    news: [], tx: [], seasonOver: false,
    clubs: CLUB_DEFS.map(([name, short, tier, c1, c2], i) => ({
      id: i, name, short, tier, c1, c2,
      budget: TIER_BUDGET[tier], morale: 70,
      formation: '4-3-3', mentality: 'balanced',
      players: genSquad(tier),
    })),
  };
  genFixtures(G);
  news(G, `👔 ${managerName} appointed manager of ${G.clubs[clubId].name}. Welcome!`);
  return G;
}

const ENG = {
  DAY, FORMATIONS, CLUB_DEFS, newGame, advanceDay, playRound, table, bestXI,
  windowOpen, bid, signPlayer, sellPlayer, completeSale, endSeason, wageBill,
  genPlayer, calcOvr, calcValue, refresh, news,
};
if (typeof module !== 'undefined') module.exports = ENG;
