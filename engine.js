// engine.js — pure game logic over the real FC26 dataset (data.js).
// Runs in browser (globals) and node (module.exports).
'use strict';
const DB = typeof module !== 'undefined' ? require('./data.js') : DATA;

const DAY = 86400000;
const R = n => Math.floor(Math.random() * n);
const rnd = (a, b) => a + Math.random() * (b - a);
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const pick = a => a[R(a.length)];
const shuffle = a => { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = R(i + 1); [a[i], a[j]] = [a[j], a[i]]; } return a; };

// ---------- youth name pools (academy regens only — senior players are real) ----------
const NAMES = {
  England: { f: ['Jack', 'Harry', 'Ollie', 'George', 'Lewis', 'Callum', 'Mason', 'Reece', 'Kyle', 'Aaron', 'Ben', 'Joe'], l: ['Walker', 'Hughes', 'Baker', 'Turner', 'Clark', 'Ward', 'Foster', 'Gibson', 'Hall', 'Dawson', 'Reid', 'Cole'] },
  Spain: { f: ['Pablo', 'Sergio', 'Iker', 'Dani', 'Alvaro', 'Marco', 'Hugo', 'Adrian', 'Raul', 'Javi', 'Nico', 'Pedro'], l: ['Garcia', 'Torres', 'Navarro', 'Moreno', 'Vazquez', 'Serrano', 'Ortega', 'Ramos', 'Gil', 'Castro', 'Rubio', 'Molina'] },
  Germany: { f: ['Leon', 'Finn', 'Jonas', 'Lukas', 'Felix', 'Niklas', 'Tim', 'Moritz', 'Jan', 'Erik', 'Til', 'Kai'], l: ['Muller', 'Schmidt', 'Weber', 'Wagner', 'Becker', 'Hoffmann', 'Schulz', 'Koch', 'Richter', 'Klein', 'Wolf', 'Braun'] },
  Italy: { f: ['Luca', 'Marco', 'Matteo', 'Alessandro', 'Davide', 'Federico', 'Gabriele', 'Lorenzo', 'Nicolo', 'Riccardo', 'Simone', 'Tommaso'], l: ['Rossi', 'Russo', 'Ferrari', 'Esposito', 'Bianchi', 'Romano', 'Colombo', 'Ricci', 'Greco', 'Conti', 'Gallo', 'Mancini'] },
  France: { f: ['Kylian', 'Antoine', 'Theo', 'Hugo', 'Lucas', 'Jules', 'Enzo', 'Mathis', 'Noah', 'Leo', 'Rayan', 'Malo'], l: ['Martin', 'Bernard', 'Dubois', 'Moreau', 'Laurent', 'Girard', 'Lambert', 'Fontaine', 'Rousseau', 'Mercier', 'Blanc', 'Renard'] },
  Portugal: { f: ['Joao', 'Diogo', 'Tiago', 'Goncalo', 'Rui', 'Andre', 'Bruno', 'Rafael', 'Miguel', 'Vasco', 'Duarte', 'Afonso'], l: ['Silva', 'Santos', 'Ferreira', 'Pereira', 'Costa', 'Rodrigues', 'Martins', 'Sousa', 'Fernandes', 'Gomes', 'Lopes', 'Carvalho'] },
  'Saudi Arabia': { f: ['Salem', 'Fahad', 'Abdullah', 'Saud', 'Khalid', 'Nawaf', 'Turki', 'Faisal', 'Majed', 'Sultan', 'Yasser', 'Hattan'], l: ['Al-Dawsari', 'Al-Shehri', 'Al-Ghannam', 'Al-Bulaihi', 'Al-Najei', 'Al-Amri', 'Al-Harbi', 'Al-Otaibi', 'Al-Mutairi', 'Al-Qahtani', 'Al-Faraj', 'Al-Buraikan'] },
  USA: { f: ['Tyler', 'Brandon', 'Austin', 'Jordan', 'Caleb', 'Ethan', 'Logan', 'Dylan', 'Chase', 'Cole', 'Blake', 'Trey'], l: ['Johnson', 'Williams', 'Miller', 'Davis', 'Wilson', 'Moore', 'Taylor', 'Anderson', 'Thomas', 'Jackson', 'White', 'Harris'] },
  'Türkiye': { f: ['Emre', 'Mert', 'Burak', 'Cenk', 'Arda', 'Kerem', 'Ozan', 'Halil', 'Yusuf', 'Kaan', 'Baris', 'Umut'], l: ['Yilmaz', 'Kaya', 'Demir', 'Celik', 'Sahin', 'Aydin', 'Ozturk', 'Arslan', 'Dogan', 'Kilic', 'Aslan', 'Polat'] },
  Brazil: { f: ['Gabriel', 'Lucas', 'Matheus', 'Vinicius', 'Thiago', 'Rafael', 'Caio', 'Joao', 'Pedro', 'Eduardo', 'Felipe', 'Igor'], l: ['Silva', 'Santos', 'Oliveira', 'Souza', 'Costa', 'Pereira', 'Almeida', 'Ferreira', 'Ribeiro', 'Barbosa', 'Rocha', 'Dias'] },
  Argentina: { f: ['Julian', 'Lautaro', 'Emiliano', 'Nicolas', 'Rodrigo', 'Facundo', 'Thiago', 'Franco', 'Mateo', 'Bruno', 'Tomas', 'Valentin'], l: ['Fernandez', 'Rodriguez', 'Gonzalez', 'Lopez', 'Martinez', 'Diaz', 'Alvarez', 'Romero', 'Sosa', 'Acosta', 'Medina', 'Rojas'] },
  Nigeria: { f: ['Chidi', 'Emeka', 'Kelechi', 'Obinna', 'Sola', 'Tunde', 'Ifeanyi', 'Uche', 'Femi', 'Sam', 'David', 'Victor'], l: ['Okafor', 'Adeyemi', 'Eze', 'Okonkwo', 'Balogun', 'Ibe', 'Nwosu', 'Adebayo', 'Chukwu', 'Obi', 'Musa', 'Lawal'] },
};

// ---------- players ----------
// attr slots a[0..5]: pac/sho/pas/dri/def/phy outfield, div/han/kic/ref/spe/pos for GK
const W = { GK: [.1, .2, .1, .35, .05, .2], DF: [.10, .05, .10, .05, .45, .25], MF: [.10, .15, .30, .20, .10, .15], AT: [.20, .35, .10, .20, .02, .13] };
const SHAPE = { GK: [0, 0, -8, 4, -10, 0], DF: [-2, -18, -5, -8, 6, 4], MF: [-3, -4, 6, 4, -8, -2], AT: [5, 6, -4, 4, -25, -1] };
let nextId = 1;

function calcValue(p) {
  if (p.ovr <= 55) return 100e3;
  const ageF = p.age <= 23 ? 1.3 : p.age <= 27 ? 1.1 : p.age <= 30 ? 1.0 : p.age <= 32 ? 0.6 : 0.3;
  const potF = 1 + (p.pot - p.ovr) * 0.02;
  return Math.max(100e3, Math.round(Math.pow(p.ovr - 55, 2.9) * 3000 * ageF * potF / 1e5) * 1e5);
}

function genYouth(country) {
  const nat = Math.random() < 0.6 && NAMES[country] ? country : pick(Object.keys(NAMES));
  const n = NAMES[nat] || NAMES.England;
  const pos = pick(['DF', 'DF', 'MF', 'MF', 'AT', 'AT', 'GK']);
  const age = 16 + R(3);
  const base = 52 + rnd(0, 14);
  const p = { id: nextId++, name: pick(n.f) + ' ' + pick(n.l), nat, pos, age, img: null, fit: 100, injury: 0, apps: 0, sg: 0, sa: 0, listed: false, youth: true };
  p.a = SHAPE[pos].map(s => Math.round(clamp(base + s + rnd(-5, 5), 25, 90)));
  p.ovr = Math.round(p.a.reduce((s, v, i) => s + v * W[pos][i], 0));
  p.pot = clamp(p.ovr + 8 + R(20), p.ovr, 95);
  p.value = calcValue(p);
  p.wage = Math.max(500, Math.round(p.value / 2500 / 100) * 100);
  p.years = 3;
  return p;
}

// ---------- fixtures & dates ----------
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
function nthWeekday(y, m, wd, n) { // n>=1; m 0-11
  const d = new Date(Date.UTC(y, m, 1));
  let day = 1 + (7 + wd - d.getUTCDay()) % 7 + (n - 1) * 7;
  return Date.UTC(y, m, day);
}
function leagueDates(n, s0) { // Saturdays, spilling onto Mondays for 40+ round leagues
  const sats = Array.from({ length: 39 }, (_, k) => s0 + k * 7 * DAY);
  if (n <= 39) return sats.slice(0, n);
  const mons = [];
  for (let i = 1; i <= n - 39; i++) mons.push(s0 + Math.floor(i * 39 / (n - 38)) * 7 * DAY + 2 * DAY);
  return sats.concat(mons).sort((a, b) => a - b).slice(0, n);
}
const seasonMonth = (Y, m) => m >= 6 ? Y : Y + 1; // season Aug Y – May Y+1

const CUP_NAMES = { England: 'FA Cup', Spain: 'Copa del Rey', Germany: 'DFB-Pokal', Italy: 'Coppa Italia', France: 'Coupe de France', Portugal: 'Taça de Portugal' };
const STAGE = n => ({ 32: 'Round of 32', 16: 'Round of 16', 8: 'Quarter-final', 4: 'Semi-final', 2: 'FINAL' })[n] || 'Round';

const power = c => { // squad strength = avg of best 18 OVRs
  const t = c.players.map(p => p.ovr).sort((a, b) => b - a).slice(0, 18);
  return t.reduce((s, v) => s + v, 0) / Math.max(1, t.length);
};
const leagueClubs = (G, li) => G.clubs.filter(c => c.lg === li);

// ---------- season generation ----------
function genSeason(G) {
  const Y = G.year;
  G.fixtures = []; G.knock = {}; G.groups = {};
  const s0 = nthWeekday(Y, 7, 6, 3); // 3rd Saturday of Aug
  // leagues (MLS 30 clubs: single round-robin, everyone else double)
  DB.leagues.forEach((L, li) => {
    const ids = leagueClubs(G, li).map(c => c.id);
    let rounds = roundRobin(shuffle(ids));
    if (ids.length < 26) rounds = rounds.concat(rounds.map(rd => rd.map(([h, a]) => [a, h]))); // MLS (30 clubs) plays single round-robin
    const dates = leagueDates(rounds.length, s0);
    rounds.forEach((rd, r) => rd.forEach(([h, a]) =>
      G.fixtures.push({ c: 'L' + li, r: r + 1, t: dates[r], h, a, hg: 0, ag: 0, pl: false })));
  });
  // domestic cups: 32 entrants (all D1 + best of D2), Wednesdays
  const cupWeds = [[8, 2], [9, 2], [10, 2], [2, 2], [4, 3]].map(([m, n]) => nthWeekday(seasonMonth(Y, m), m, 3, n));
  G.cupCountries = DB.leagues.map((L, li) => L.play && L.level === 1 ? li : -1).filter(li => li >= 0);
  for (const li of G.cupCountries) {
    const L = DB.leagues[li];
    let entrants = leagueClubs(G, li);
    if (L.d2 != null) entrants = entrants.concat(leagueClubs(G, L.d2).sort((a, b) => power(b) - power(a)).slice(0, 32 - entrants.length));
    const size = entrants.length >= 32 ? 32 : 16;
    entrants = entrants.sort((a, b) => power(b) - power(a)).slice(0, size);
    G.knock['C' + li] = { name: CUP_NAMES[L.country], flag: L.flag, alive: entrants.map(c => c.id), dates: cupWeds.slice(5 - Math.log2(size)), round: 0 };
    drawRound(G, 'C' + li);
  }
  // Europe: UCL + UEL groups (Tue / Thu), knockout later
  const slots = { 'Premier League': 4, 'La Liga': 4, 'Bundesliga': 4, 'Serie A': 4, 'Ligue 1': 3, 'Primeira Liga': 2, 'Süper Lig': 2 };
  const ranked = li => (G.lastTables && G.lastTables[li] || leagueClubs(G, li).sort((a, b) => power(b) - power(a)).map(c => c.id))
    .filter(id => DB.leagues[G.clubs[id].lg].level === 1); // relegated clubs don't play in Europe
  let ucl = [], uel = [];
  for (const [li, L] of DB.leagues.entries()) {
    if (!L.uefa) continue;
    const ids = ranked(li), n = slots[L.name] || 2;
    ucl.push(...ids.slice(0, n));
    uel.push(...ids.slice(n, n + 3));
  }
  const rest = DB.leagues.flatMap((L, li) => L.uefa ? ranked(li) : []).filter(id => !ucl.includes(id) && !uel.includes(id))
    .sort((a, b) => power(G.clubs[b]) - power(G.clubs[a]));
  while (ucl.length < 32) ucl.push(uel.length ? uel.shift() : rest.shift());
  while (uel.length < 32) uel.push(rest.shift());
  const groupDays = wd => [[8, 3], [9, 1], [9, 4], [10, 2], [11, 1], [11, 2]].map(([m, n]) => nthWeekday(seasonMonth(Y, m), m, wd, n));
  const koDays = wd => [[1, 3], [3, 2], [3, 4]].map(([m, n]) => nthWeekday(seasonMonth(Y, m), m, wd, n));
  for (const [comp, teams, wd] of [['UCL', ucl, 2], ['UEL', uel, 4]]) {
    const pots = [0, 1, 2, 3].map(i => shuffle(teams.slice().sort((a, b) => power(G.clubs[b]) - power(G.clubs[a])).slice(i * 8, i * 8 + 8)));
    G.groups[comp] = Array.from({ length: 8 }, (_, g) => pots.map(pot => pot[g]));
    const dates = groupDays(wd);
    G.groups[comp].forEach((grp, gi) => {
      const rr = roundRobin(grp);
      rr.concat(rr.map(rd => rd.map(([h, a]) => [a, h]))).forEach((rd, r) =>
        rd.forEach(([h, a]) => G.fixtures.push({ c: comp + 'g', g: gi, r: r + 1, t: dates[r], h, a, hg: 0, ag: 0, pl: false })));
    });
    G.knock[comp] = { name: comp === 'UCL' ? 'Champions League' : 'Europa League', flag: '⭐', alive: null, // seeded after groups
      dates: koDays(wd).concat(nthWeekday(Y + 1, 4, 6, 4) + (comp === 'UEL' ? -2 * DAY : 0)), round: 0 };
  }
  G.seasonOver = false;
  G.expect = boardExpectation(G);
}

function boardExpectation(G) {
  const c = G.clubs[G.userClub], L = DB.leagues[c.lg];
  const ranked = leagueClubs(G, c.lg).sort((a, b) => power(b) - power(a));
  const rank = ranked.indexOf(c) + 1, n = ranked.length;
  if (L.level === 2) return rank <= 4 ? { txt: 'Win promotion', pos: 3 } : { txt: 'Finish in the top half', pos: Math.ceil(n / 2) };
  if (rank <= 2) return { txt: 'Win the league title', pos: 1 };
  if (rank <= 4) return { txt: 'Qualify for the Champions League', pos: 4 };
  if (rank <= 8) return { txt: 'Qualify for Europe', pos: 7 };
  if (rank <= n - 6) return { txt: 'A solid mid-table finish', pos: n - 8 };
  return { txt: 'Stay clear of the relegation zone', pos: n - 3 };
}
function acceptJob(G, id) {
  G.userClub = id;
  G.expect = boardExpectation(G);
  news(G, `👔 ${G.managerName} appointed manager of ${G.clubs[id].n}!`);
}

function drawRound(G, comp) {
  const K = G.knock[comp];
  const t = K.dates[K.round];
  const order = shuffle(K.alive);
  for (let i = 0; i < order.length; i += 2)
    G.fixtures.push({ c: comp, r: K.round + 1, stage: STAGE(order.length), t, h: order[i], a: order[i + 1], hg: 0, ag: 0, pl: false });
}

// knockout ties can't end level: penalties, slightly biased to the stronger side
function settleTie(G, f) {
  if (f.hg !== f.ag) return f.hg > f.ag ? f.h : f.a;
  f.pen = Math.random() < 0.5 + (power(G.clubs[f.h]) - power(G.clubs[f.a])) * 0.02 ? f.h : f.a;
  return f.pen;
}

const EURO_PRIZE = { UCL: [10e6, 12e6, 15e6, 25e6], UEL: [4e6, 5e6, 6e6, 10e6] };
function progressComps(G) {
  // group stages done → seed knockouts
  for (const comp of ['UCL', 'UEL']) {
    const K = G.knock[comp];
    if (!K.alive && G.fixtures.filter(f => f.c === comp + 'g').every(f => f.pl)) {
      K.alive = G.groups[comp].flatMap((grp, gi) => table(G, comp + 'g', grp, gi).slice(0, 2).map(r => r.id));
      drawRound(G, comp);
      news(G, `⭐ ${K.name} group stage complete — knockout rounds drawn.`);
    }
  }
  // knockout rounds done → next round or champion
  for (const [comp, K] of Object.entries(G.knock)) {
    if (!K.alive || K.alive.length < 2) continue;
    const cur = G.fixtures.filter(f => f.c === comp && f.r === K.round + 1);
    if (!cur.length || !cur.every(f => f.pl)) continue;
    K.alive = cur.map(f => settleTie(G, f));
    K.round++;
    const prize = EURO_PRIZE[comp];
    if (prize) for (const id of K.alive) G.clubs[id].budget += prize[Math.min(K.round - 1, 3)];
    if (K.alive.length === 1) {
      const winner = G.clubs[K.alive[0]];
      winner.budget += prize ? prize[3] : 5e6;
      winner.morale = clamp(winner.morale + 10, 30, 99);
      news(G, `🏆 ${winner.n} win the ${K.name}!`);
      if (winner.id === G.userClub) {
        G.trophies.push(`${K.name} — ${G.year}/${(G.year + 1) % 100}`);
        G.rep = clamp(G.rep + (comp === 'UCL' ? 15 : comp === 'UEL' ? 8 : 5), 0, 100);
      }
    } else drawRound(G, comp);
  }
}

// ---------- selection & match sim ----------
// FC26-style player roles. Each kind (position type) has a set of Roles; each Role
// has allowed Focuses. atk/def are the role's off-ball contribution (0..8); focus tweaks it.
const KIND_LINE = { GK: 'GK', CB: 'DF', FB: 'DF', CDM: 'MF', CM: 'MF', CAM: 'MF', WM: 'MF', WF: 'AT', ST: 'AT' };
const KIND_LABEL = { GK: 'GK', CB: 'CB', FB: 'FB', CDM: 'CDM', CM: 'CM', CAM: 'CAM', WM: 'WM', WF: 'WF', ST: 'ST' };
const ROLE_CATALOG = {
  GK: { 'Goalkeeper': { atk: 0, def: 3, focuses: ['Defend', 'Sweeper Keeper'] } },
  CB: {
    'Defender': { atk: 0, def: 6, focuses: ['Defend', 'Stopper'] },
    'Ball-Playing Def': { atk: 2, def: 5, focuses: ['Defend', 'Build-Up'] },
  },
  FB: {
    'Fullback': { atk: 2, def: 4, focuses: ['Defend', 'Balanced'] },
    'Falseback': { atk: 1, def: 5, focuses: ['Defend', 'Balanced'] },
    'Wingback': { atk: 4, def: 3, focuses: ['Balanced', 'Attack'] },
    'Attacking WB': { atk: 5, def: 2, focuses: ['Attack', 'Balanced'] },
    'Inverted WB': { atk: 3, def: 4, focuses: ['Defend', 'Balanced'] },
  },
  CDM: {
    'Holding': { atk: 1, def: 6, focuses: ['Defend'] },
    'Deep-Lying PM': { atk: 3, def: 4, focuses: ['Defend', 'Build-Up'] },
    'Centre-Half': { atk: 0, def: 6, focuses: ['Defend'] },
    'Wide Half': { atk: 3, def: 4, focuses: ['Defend', 'Balanced'] },
    'Box Crasher': { atk: 5, def: 2, focuses: ['Attack'] },
  },
  CM: {
    'Box-to-Box': { atk: 4, def: 4, focuses: ['Support', 'Attack', 'Defend'] },
    'Playmaker': { atk: 5, def: 2, focuses: ['Support', 'Attack', 'Roaming'] },
    'Holding': { atk: 1, def: 6, focuses: ['Defend'] },
    'Half-Winger': { atk: 5, def: 2, focuses: ['Support', 'Attack'] },
  },
  CAM: {
    'Playmaker': { atk: 6, def: 1, focuses: ['Support', 'Attack', 'Roaming'] },
    'Shadow Striker': { atk: 7, def: 1, focuses: ['Attack'] },
    'Classic 10': { atk: 6, def: 1, focuses: ['Support', 'Attack'] },
    'Half-Winger': { atk: 6, def: 1, focuses: ['Support', 'Attack'] },
  },
  WM: {
    'Winger': { atk: 5, def: 2, focuses: ['Balanced', 'Attack'] },
    'Wide Midfielder': { atk: 3, def: 4, focuses: ['Defend', 'Balanced'] },
    'Wide Playmaker': { atk: 5, def: 2, focuses: ['Support', 'Attack'] },
    'Inside Forward': { atk: 6, def: 1, focuses: ['Support', 'Attack'] },
  },
  WF: {
    'Winger': { atk: 6, def: 1, focuses: ['Balanced', 'Attack'] },
    'Inside Forward': { atk: 7, def: 1, focuses: ['Support', 'Attack'] },
    'Wide Playmaker': { atk: 6, def: 1, focuses: ['Support', 'Attack'] },
  },
  ST: {
    'Advanced Forward': { atk: 8, def: 0, focuses: ['Attack'] },
    'Poacher': { atk: 8, def: 0, focuses: ['Attack'] },
    'Target Forward': { atk: 7, def: 1, focuses: ['Support', 'Attack'] },
    'False 9': { atk: 6, def: 2, focuses: ['Support', 'Roaming'] },
  },
};
const FOCUS_DELTA = {
  'Attack': { atk: 1.5, def: -1 }, 'Defend': { atk: -1, def: 1.5 },
  'Support': { atk: 0, def: 0 }, 'Balanced': { atk: 0, def: 0 },
  'Build-Up': { atk: 1, def: 0 }, 'Roaming': { atk: 0.8, def: -0.3 },
  'Stopper': { atk: -0.5, def: 1 }, 'Sweeper Keeper': { atk: 0.5, def: -0.5 },
};
function roleStats(kind, role, focus) {
  const cat = ROLE_CATALOG[kind] || ROLE_CATALOG.CM;
  const r = cat[role] || cat[Object.keys(cat)[0]];
  const fd = FOCUS_DELTA[focus] || { atk: 0, def: 0 };
  return { atk: r.atk + fd.atk, def: r.def + fd.def };
}
function defRole(kind) {
  const role = Object.keys(ROLE_CATALOG[kind] || ROLE_CATALOG.CM)[0];
  return { role, focus: (ROLE_CATALOG[kind][role].focuses)[0], kind };
}
// Formations as 11 pitch slots. x: 0(left)..100(right); y: 0(opponent goal)..100(own goal).
const S = (x, y, kind) => ({ x, y, kind, line: KIND_LINE[kind] });
const FORMATION_DEF = {
  '4-3-3': [S(50, 90, 'GK'), S(16, 72, 'FB'), S(39, 75, 'CB'), S(61, 75, 'CB'), S(84, 72, 'FB'), S(50, 58, 'CDM'), S(30, 47, 'CM'), S(70, 47, 'CM'), S(18, 26, 'WF'), S(50, 20, 'ST'), S(82, 26, 'WF')],
  '4-4-2': [S(50, 90, 'GK'), S(14, 72, 'FB'), S(37, 74, 'CB'), S(63, 74, 'CB'), S(86, 72, 'FB'), S(14, 48, 'WM'), S(38, 50, 'CM'), S(62, 50, 'CM'), S(86, 48, 'WM'), S(38, 22, 'ST'), S(62, 22, 'ST')],
  '4-2-3-1': [S(50, 90, 'GK'), S(14, 72, 'FB'), S(37, 74, 'CB'), S(63, 74, 'CB'), S(86, 72, 'FB'), S(38, 60, 'CDM'), S(62, 60, 'CDM'), S(17, 38, 'WM'), S(50, 36, 'CAM'), S(83, 38, 'WM'), S(50, 20, 'ST')],
  '4-3-2-1': [S(50, 90, 'GK'), S(14, 72, 'FB'), S(37, 74, 'CB'), S(63, 74, 'CB'), S(86, 72, 'FB'), S(50, 58, 'CDM'), S(32, 49, 'CM'), S(68, 49, 'CM'), S(36, 33, 'CAM'), S(64, 33, 'CAM'), S(50, 19, 'ST')],
  '4-1-2-1-2': [S(50, 90, 'GK'), S(14, 72, 'FB'), S(37, 74, 'CB'), S(63, 74, 'CB'), S(86, 72, 'FB'), S(50, 60, 'CDM'), S(28, 48, 'CM'), S(72, 48, 'CM'), S(50, 34, 'CAM'), S(40, 20, 'ST'), S(60, 20, 'ST')],
  '4-5-1': [S(50, 90, 'GK'), S(14, 72, 'FB'), S(37, 74, 'CB'), S(63, 74, 'CB'), S(86, 72, 'FB'), S(12, 50, 'WM'), S(33, 51, 'CM'), S(50, 57, 'CDM'), S(67, 51, 'CM'), S(88, 50, 'WM'), S(50, 20, 'ST')],
  '4-1-4-1': [S(50, 90, 'GK'), S(14, 72, 'FB'), S(37, 74, 'CB'), S(63, 74, 'CB'), S(86, 72, 'FB'), S(50, 60, 'CDM'), S(14, 45, 'WM'), S(38, 47, 'CM'), S(62, 47, 'CM'), S(86, 45, 'WM'), S(50, 20, 'ST')],
  '4-4-1-1': [S(50, 90, 'GK'), S(14, 72, 'FB'), S(37, 74, 'CB'), S(63, 74, 'CB'), S(86, 72, 'FB'), S(14, 50, 'WM'), S(38, 51, 'CM'), S(62, 51, 'CM'), S(86, 50, 'WM'), S(50, 33, 'CAM'), S(50, 19, 'ST')],
  '3-5-2': [S(50, 90, 'GK'), S(30, 74, 'CB'), S(50, 76, 'CB'), S(70, 74, 'CB'), S(11, 52, 'FB'), S(34, 50, 'CM'), S(50, 58, 'CDM'), S(66, 50, 'CM'), S(89, 52, 'FB'), S(40, 22, 'ST'), S(60, 22, 'ST')],
  '3-4-3': [S(50, 90, 'GK'), S(30, 74, 'CB'), S(50, 76, 'CB'), S(70, 74, 'CB'), S(13, 50, 'WM'), S(40, 51, 'CM'), S(60, 51, 'CM'), S(87, 50, 'WM'), S(20, 24, 'WF'), S(50, 20, 'ST'), S(80, 24, 'WF')],
  '5-3-2': [S(50, 90, 'GK'), S(9, 66, 'FB'), S(30, 75, 'CB'), S(50, 77, 'CB'), S(70, 75, 'CB'), S(91, 66, 'FB'), S(31, 49, 'CM'), S(50, 55, 'CDM'), S(69, 49, 'CM'), S(40, 22, 'ST'), S(60, 22, 'ST')],
  '5-4-1': [S(50, 90, 'GK'), S(9, 66, 'FB'), S(30, 75, 'CB'), S(50, 77, 'CB'), S(70, 75, 'CB'), S(91, 66, 'FB'), S(14, 50, 'WM'), S(38, 51, 'CM'), S(62, 51, 'CM'), S(86, 50, 'WM'), S(50, 20, 'ST')],
};
const FORMATIONS = FORMATION_DEF; // keeps ENG.FORMATIONS as the source of formation keys
function applyFormation(c, key) {
  if (!FORMATION_DEF[key]) key = '4-3-3';
  c.formation = key;
  c.shape = FORMATION_DEF[key].map(s => ({ x: s.x, y: s.y, kind: s.kind, line: s.line }));
  c.roles = c.shape.map(s => defRole(s.kind));
  c.picks = new Array(11).fill(null);
}
function ensureTactics(c) {
  if (!FORMATION_DEF[c.formation]) c.formation = '4-3-3';
  if (!c.shape || c.shape.length !== 11 || !c.roles || c.roles.length !== 11) applyFormation(c, c.formation);
  if (!c.buildUp) c.buildUp = c.preset === 'counter' ? 'counter' : c.preset === 'possession' ? 'slow' : 'balanced';
  if (!['deep', 'balanced', 'high', 'aggressive'].includes(c.defApproach))
    c.defApproach = ['deep', 'aggressive'].includes(c.defAppr) ? c.defAppr : 'balanced';
  if (!['narrow', 'balanced', 'wide'].includes(c.width)) c.width = 'balanced';
  if (!Array.isArray(c.picks) || c.picks.length !== 11) c.picks = new Array(11).fill(null);
}
// How well a player's attributes [pac,sho,pas,dri,def,phy] suit a slot kind — used to
// arrange the chosen XI so wide players go wide and defenders stay central.
function kindScore(p, kind) {
  const A = p.a;
  switch (kind) {
    case 'CB': return A[4] * 2 + A[5];
    case 'FB': return A[4] + A[0] + A[3];
    case 'CDM': return A[4] * 1.4 + A[2];
    case 'CM': return A[2] + A[3] + A[4] * 0.5;
    case 'CAM': return A[2] + A[3] + A[1];
    case 'WM': return A[0] + A[3] + A[2];
    case 'WF': return A[0] + A[3] + A[1];
    case 'ST': return A[1] * 2 + A[0];
    default: return p.ovr;
  }
}
// Assemble the XI aligned to the formation slots (so the pitch draws each man at his spot).
// c.picks[i] pins a specific player to slot i (manual selection); the rest auto-fill by fit.
function lineup(c) {
  ensureTactics(c);
  const fit = c.players.filter(p => !p.injury).sort((x, y) => y.ovr * y.fit - x.ovr * x.fit);
  const byId = new Map(c.players.map(p => [p.id, p]));
  const used = new Set(), assigned = new Array(11).fill(null);
  const slots = c.shape.map((s, i) => ({ x: s.x, y: s.y, kind: s.kind, line: s.line, idx: i }));
  c.picks.forEach((pid, i) => { // honour manual picks first
    if (pid == null) return;
    const p = byId.get(pid);
    if (p && !p.injury && !used.has(p.id)) { assigned[i] = p; used.add(p.id); }
  });
  for (const line of ['GK', 'DF', 'MF', 'AT']) {
    const lineSlots = slots.filter(s => s.line === line && !assigned[s.idx]);
    const picks = [];
    for (const p of fit) { if (picks.length >= lineSlots.length) break; if (!used.has(p.id) && p.pos === line) { picks.push(p); used.add(p.id); } }
    for (const s of lineSlots) { // greedily give each slot its best-fitting available pick
      if (!picks.length) break;
      let bi = 0, best = -1;
      picks.forEach((p, j) => { const sc = kindScore(p, s.kind); if (sc > best) { best = sc; bi = j; } });
      assigned[s.idx] = picks.splice(bi, 1)[0];
    }
  }
  const pool = fit.concat(c.players); // backfill empty slots (thin squad / injuries)
  slots.forEach(s => { if (assigned[s.idx]) return; const p = pool.find(p => !used.has(p.id)); if (p) { assigned[s.idx] = p; used.add(p.id); } });
  return c.shape.map((s, i) => ({ x: s.x, y: s.y, kind: s.kind, line: s.line, role: c.roles[i].role, focus: c.roles[i].focus, player: assigned[i] }));
}
function bestXI(c) { return lineup(c).map(l => l.player).filter(Boolean); }
function strength(c, xi, home) {
  const avgOvr = xi.reduce((s, p) => s + p.ovr, 0) / xi.length;
  const avgFit = xi.reduce((s, p) => s + p.fit, 0) / xi.length;
  const ment = c.mentality === 'attacking' ? 2 : c.mentality === 'defensive' ? -2 : 0;
  return avgOvr + (c.morale - 70) / 10 + (avgFit - 85) / 10 + (home ? 2.5 : 0) + ment;
}
// Team profile derived from roles + shape + build-up + defensive approach.
// attack = own chance-creation multiplier; openness = chances conceded multiplier.
const REF_ATK = 28, REF_DEF = 48, REF_ADV = 46; // calibrated so a default-role team centers on 1.0/1.0
const BUILD = { balanced: { atk: 0, open: 0 }, counter: { atk: -0.05, open: -0.04 }, slow: { atk: -0.02, open: -0.06 } };
const APPR = { deep: { atk: -0.02, open: -0.10 }, balanced: { atk: 0, open: 0 }, high: { atk: 0.04, open: 0.08 }, aggressive: { atk: 0.06, open: 0.12 } };
const WIDTHS = { narrow: { atk: 0, open: -0.02 }, balanced: { atk: 0, open: 0 }, wide: { atk: 0.03, open: 0.02 } };
function teamProfile(L, c) {
  let atk = 0, def = 0, adv = 0, n = 0;
  for (const l of L) {
    const rs = roleStats(l.kind, l.role, l.focus);
    atk += rs.atk; def += rs.def;
    if (l.kind !== 'GK') { adv += (100 - l.y); n++; }
  }
  const atkIdx = atk / REF_ATK, defIdx = def / REF_DEF, advIdx = (adv / Math.max(1, n)) / REF_ADV;
  const bu = BUILD[c.buildUp] || BUILD.balanced, ap = APPR[c.defApproach] || APPR.balanced, wd = WIDTHS[c.width] || WIDTHS.balanced;
  const attack = clamp(1 + 0.34 * (atkIdx - 1) + 0.20 * (advIdx - 1) + bu.atk + ap.atk + wd.atk, 0.72, 1.35);
  const openness = clamp(1 + 0.30 * (atkIdx - 1) - 0.34 * (defIdx - 1) + 0.12 * (advIdx - 1) + bu.open + ap.open + wd.open, 0.68, 1.45);
  return { attack, openness, counter: c.buildUp === 'counter', atkIdx, defIdx, advIdx };
}
function simMatch(G, hc, ac, detailed) {
  const hL = lineup(hc), aL = lineup(ac);
  const hXI = hL.map(l => l.player).filter(Boolean), aXI = aL.map(l => l.player).filter(Boolean);
  const hs = strength(hc, hXI, true), as = strength(ac, aXI, false);
  const hP = teamProfile(hL, hc), aP = teamProfile(aL, ac);
  const hMult = hP.attack * aP.openness * (hP.counter && hs < as ? 1.18 : 1);
  const aMult = aP.attack * hP.openness * (aP.counter && as < hs ? 1.18 : 1);
  let hg = 0, ag = 0;
  const ev = [], scorers = { h: [], a: [] }, plays = [];
  const stats = { h: { shots: 0, sot: 0 }, a: { shots: 0, sot: 0 } };
  const pickScorer = L => {
    const pool = L.filter(l => l.player).flatMap(l => Array(Math.max(0, Math.round(roleStats(l.kind, l.role, l.focus).atk * 1.1))).fill(l.player));
    return pool.length ? pick(pool) : (L.find(l => l.player) || {}).player;
  };
  for (let min = 1; min <= 90; min++) {
    for (const side of ['h', 'a']) {
      const my = side === 'h' ? hs : as, opp = side === 'h' ? as : hs;
      const c = side === 'h' ? hc : ac, xi = side === 'h' ? hXI : aXI;
      const r = clamp((my - 50) / (opp - 50), 0.5, 2.0); // subtract a floor so OVR gaps actually separate teams
      if (Math.random() < 0.125 * r * r * (side === 'h' ? hMult : aMult)) {
        const shooter = pickScorer(side === 'h' ? hL : aL);
        stats[side].shots++;
        if (Math.random() < 0.105 * r) {
          stats[side].sot++;
          side === 'h' ? hg++ : ag++;
          shooter.sg++;
          scorers[side].push(shooter.name + " " + min + "'");
          plays.push({ min, side, out: 'goal', name: shooter.name });
          let txt = `⚽ ${min}' GOAL! ${shooter.name} scores for ${c.s}!`;
          const mates = xi.filter(p => p !== shooter && p.pos !== 'GK');
          if (Math.random() < 0.65 && mates.length) { const a2 = pick(mates); a2.sa++; txt += ` (assist: ${a2.name})`; }
          ev.push({ min, txt, goal: side, score: `${hg}-${ag}` });
        } else {
          const onT = Math.random() < 0.35;
          if (onT) stats[side].sot++;
          plays.push({ min, side, out: onT ? 'save' : 'miss', name: shooter.name });
          if (detailed && Math.random() < 0.25)
            ev.push({ min, txt: `${min}' ${shooter.name} (${c.s}) shoots — ${pick(['saved!', 'just wide!', 'off the bar!', 'blocked!'])}` });
        }
      }
    }
  }
  const ratings = [];
  for (const [c, xi, gf, ga] of [[hc, hXI, hg, ag], [ac, aXI, ag, hg]]) {
    const res = gf > ga ? 1 : gf < ga ? -1 : 0;
    c.morale = clamp(c.morale + res * 4 + (res === 0 ? 1 : 0), 30, 95);
    for (const p of xi) {
      p.apps++;
      p.fit = clamp(p.fit - rnd(8, 15), 20, 100);
      if (Math.random() < 0.035) { p.injury = 5 + R(25); if (detailed) ev.push({ min: 90, txt: `🩹 ${p.name} (${c.s}) picked up an injury (${p.injury} days).` }); }
      const g = scorers.h.concat(scorers.a).filter(s => s.startsWith(p.name + ' ')).length;
      if (detailed) ratings.push({ club: c.id, name: p.name, pos: p.pos, img: p.img, ovr: p.ovr, r: Math.round(clamp(6.4 + g * 1.2 + res * 0.4 + rnd(-0.7, 0.7), 4, 10) * 10) / 10 });
    }
  }
  stats.h.poss = Math.round(clamp(50 + (hs - as) * 2.2 + (hc.preset === 'possession' ? 5 : 0) - (ac.preset === 'possession' ? 5 : 0), 30, 70));
  stats.a.poss = 100 - stats.h.poss;
  const snapXI = xi => xi.map(p => ({ name: p.name, pos: p.pos, ovr: p.ovr }));
  return { hg, ag, ev, scorers, ratings, stats, plays, xis: detailed ? { h: snapXI(hXI), a: snapXI(aXI) } : null };
}

function playDay(G) {
  const todays = G.fixtures.filter(f => f.t === G.time && !f.pl);
  const out = { others: [], user: null };
  for (const f of todays) {
    const hc = G.clubs[f.h], ac = G.clubs[f.a];
    const isUser = f.h === G.userClub || f.a === G.userClub;
    const res = simMatch(G, hc, ac, isUser);
    f.hg = res.hg; f.ag = res.ag; f.pl = true;
    if (isUser) {
      out.user = { f, ...res };
      const me = G.clubs[G.userClub];
      if (f.h === G.userClub) {
        const gate = Math.round(clamp(initialBudget(me) * 0.03, 50e3, 5e6) / 1e4) * 1e4;
        me.budget += gate;
        G.tx.push({ t: G.time, txt: 'Matchday gate receipts', amt: gate });
      }
    } else out.others.push(f);
  }
  if (todays.length) progressComps(G);
  if (G.fixtures.every(f => f.pl)) G.seasonOver = true;
  return out;
}

// ---------- tables ----------
function table(G, comp, subset, group) {
  const clubs = subset ? subset.map(id => G.clubs[id]) : leagueClubs(G, +comp.slice(1));
  const rows = new Map(clubs.map(c => [c.id, { id: c.id, name: c.n, short: c.s, p: 0, w: 0, d: 0, l: 0, gf: 0, ga: 0, pts: 0 }]));
  for (const f of G.fixtures) {
    if (f.c !== comp || !f.pl || (group !== undefined && f.g !== group)) continue;
    const h = rows.get(f.h), a = rows.get(f.a);
    if (!h || !a) continue;
    h.p++; a.p++; h.gf += f.hg; h.ga += f.ag; a.gf += f.ag; a.ga += f.hg;
    if (f.hg > f.ag) { h.w++; h.pts += 3; a.l++; }
    else if (f.hg < f.ag) { a.w++; a.pts += 3; h.l++; }
    else { h.d++; a.d++; h.pts++; a.pts++; }
  }
  return [...rows.values()].sort((x, y) => y.pts - x.pts || (y.gf - y.ga) - (x.gf - x.ga) || y.gf - x.gf);
}

// ---------- calendar ----------
const windowOpen = G => [0, 5, 6, 7].includes(new Date(G.time).getUTCMonth()); // Jan + Jun–Aug
const wageBill = c => c.players.reduce((s, p) => s + p.wage, 0);
function news(G, txt) { G.news.unshift({ t: G.time, txt }); if (G.news.length > 80) G.news.length = 80; }

function advanceDay(G) {
  G.time += DAY;
  const d = new Date(G.time);
  for (const c of G.clubs) for (const p of c.players) {
    if (p.injury > 0) p.injury--;
    p.fit = clamp(p.fit + 3, 20, 100);
  }
  const me = G.clubs[G.userClub];
  me.budget -= wageBill(me) / 7;
  if (d.getUTCDate() === 1) { // monthly broadcast money keeps real wage bills payable
    const TV = { 'Premier League': 12e6, 'La Liga': 8e6, 'Bundesliga': 7e6, 'Serie A': 6.5e6, 'Ligue 1': 5e6, 'Primeira Liga': 2.5e6, 'Saudi Pro League': 6e6, 'MLS': 3e6, 'Süper Lig': 2e6 };
    const tv = TV[DB.leagues[me.lg].name] || 1e6;
    me.budget += tv;
    G.tx.push({ t: G.time, txt: 'Broadcast revenue', amt: tv });
  }
  if ((d.getUTCMonth() === 8 || d.getUTCMonth() === 1) && d.getUTCDate() === 1) news(G, '🚪 The transfer window has closed.');
  if (G.seasonOver) return 'seasonEnd';
  if (G.fixtures.some(f => f.t === G.time && !f.pl)) {
    if (G.fixtures.some(f => f.t === G.time && !f.pl && (f.h === G.userClub || f.a === G.userClub))) return 'match';
    playDay(G); // world plays on without you
  }
  if (windowOpen(G)) { // after fixtures so an offer never swallows a match day
    if (R(3) === 0) aiTransfers(G, 4);
    if (Math.random() < 0.05 && makeOffer(G)) return 'offer';
  }
  return null;
}

// ---------- AI transfers ----------
function aiTransfers(G, n) {
  for (let i = 0; i < n; i++) {
    const buyer = pick(G.clubs);
    if (buyer.id === G.userClub || buyer.players.length >= 32) continue;
    const L = DB.leagues[buyer.lg];
    const pw = power(buyer);
    const cands = [];
    for (const seller of G.clubs) {
      if (seller.id === buyer.id || seller.id === G.userClub || seller.players.length <= 19) continue;
      for (const p of seller.players) {
        if (p.value > buyer.budget * (L.rich ? 1 : 0.7)) continue;
        if (L.rich ? (p.ovr < 80 || p.age < 25) : L.name === 'MLS' ? p.age < 30 && p.ovr > pw + 4 : Math.abs(p.ovr - pw) > 6) continue;
        cands.push([p, seller]);
      }
    }
    if (!cands.length) continue;
    const [p, seller] = pick(cands);
    const fee = Math.round(p.value * (L.rich ? rnd(1.3, 1.8) : rnd(0.95, 1.3)));
    if (fee > buyer.budget) continue;
    seller.players.splice(seller.players.indexOf(p), 1);
    buyer.players.push(p);
    buyer.budget -= fee; seller.budget += fee;
    p.years = 2 + R(3); p.listed = false;
    if (p.ovr >= 82 || fee >= 40e6) news(G, `🔁 ${p.name} (${p.ovr}) joins ${buyer.n} from ${seller.n} for €${(fee / 1e6).toFixed(1)}M.`);
  }
}
function makeOffer(G) { // AI bids for the user's stars during windows
  const me = G.clubs[G.userClub];
  const stars = me.players.slice().sort((a, b) => b.value - a.value).slice(0, 4);
  const p = pick(stars);
  if (!p || p.value < 2e6) return false;
  const rich = Math.random() < 0.4;
  const pool = G.clubs.filter(c => c.id !== G.userClub && (rich ? DB.leagues[c.lg].rich : power(c) >= p.ovr - 4) && c.budget > p.value);
  if (!pool.length) return false;
  const buyer = pick(pool);
  const fee = Math.round(p.value * (DB.leagues[buyer.lg].rich ? rnd(1.3, 2.0) : rnd(0.9, 1.2)) / 1e5) * 1e5;
  G.pendingOffer = { cid: buyer.id, pid: p.id, fee };
  return true;
}
function acceptOffer(G) {
  const { cid, pid, fee } = G.pendingOffer;
  const me = G.clubs[G.userClub], buyer = G.clubs[cid];
  const p = me.players.find(p => p.id === pid);
  G.pendingOffer = null;
  if (!p) return;
  me.players.splice(me.players.indexOf(p), 1);
  buyer.players.push(p);
  me.budget += fee; buyer.budget -= fee;
  G.tx.push({ t: G.time, txt: `Sold ${p.name} to ${buyer.n}`, amt: fee });
  news(G, `💰 ${p.name} sold to ${buyer.n} for €${(fee / 1e6).toFixed(1)}M.`);
}

// ---------- user transfers ----------
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
  news(G, `✍️ ${p.name} signs for ${me.n} for €${(fee / 1e6).toFixed(1)}M!`);
}
function sellPlayer(G, p) {
  const buyer = pick(G.clubs.filter(c => c.id !== G.userClub));
  const fee = Math.round(p.value * rnd(0.8, 1.05) / 1e5) * 1e5;
  return { buyer, fee };
}
function completeSale(G, p, buyer, fee) {
  const me = G.clubs[G.userClub];
  me.players.splice(me.players.indexOf(p), 1);
  buyer.players.push(p);
  me.budget += fee;
  G.tx.push({ t: G.time, txt: 'Sold ' + p.name + ' to ' + buyer.n, amt: fee });
  news(G, `💰 ${p.name} sold to ${buyer.n} for €${(fee / 1e6).toFixed(1)}M.`);
}

// ---------- season end ----------
function developPlayer(p) {
  let d = 0;
  if (p.age <= 21) d = rnd(1, 4); else if (p.age <= 27) d = rnd(0, 2);
  else if (p.age >= 33) d = -rnd(2, 4); else if (p.age >= 31) d = -rnd(0, 2);
  if (d > 0) d = Math.min(d, p.pot - p.ovr);
  d = Math.round(d);
  p.ovr = clamp(p.ovr + d, 30, 99);
  p.a = p.a.map(v => Math.round(clamp(v + d * rnd(0.7, 1.3), 20, 99)));
  p.value = calcValue(p);
}

function endSeason(G) {
  const me = G.clubs[G.userClub];
  const userLg = me.lg, L = DB.leagues[userLg];
  G.lastTables = {};
  const champions = [];
  DB.leagues.forEach((LL, li) => {
    const tab = table(G, 'L' + li);
    G.lastTables[li] = tab.map(r => r.id);
    if (LL.level === 1) champions.push(`${LL.flag} ${LL.name}: ${tab[0].name}`);
    if (li === userLg) {
      G.userPos = tab.findIndex(r => r.id === G.userClub) + 1;
      if (G.userPos === 1) {
        G.trophies.push(`${LL.name} Champions — ${G.year}/${(G.year + 1) % 100}`);
        G.rep = clamp(G.rep + (LL.level === 1 ? 10 : 5), 0, 100);
      }
    }
  });
  const prize = Math.round((leagueClubs(G, userLg).length - G.userPos + 1) * (L.level === 1 ? 2e6 : 0.5e6) * (L.name === 'Premier League' ? 2 : 1));
  me.budget += prize;
  G.tx.push({ t: G.time, txt: `Season ${G.season} prize money (finished ${G.userPos})`, amt: prize });
  G.rep = clamp(G.rep + (G.userPos <= 4 ? 3 : G.userPos <= 10 ? 1 : -2), 0, 100);
  // board verdict on the season objective
  const board = { ...G.expect, met: G.userPos <= G.expect.pos };
  G.rep = clamp(G.rep + (board.met ? 3 : -3), 0, 100);
  // promotion & relegation (bottom 3 ↔ top 3; nobody drops out of D2)
  const proms = [];
  DB.leagues.forEach((LL, li) => {
    if (LL.d2 == null) return;
    const down = G.lastTables[li].slice(-3), up = G.lastTables[LL.d2].slice(0, 3);
    for (const id of down) G.clubs[id].lg = LL.d2;
    for (const id of up) G.clubs[id].lg = li;
    proms.push(`${LL.flag} Promoted: ${up.map(id => G.clubs[id].n).join(', ')} — Relegated: ${down.map(id => G.clubs[id].n).join(', ')}`);
  });
  // awards from the user's league (all-competition stats)
  const lgPlayers = leagueClubs(G, userLg).flatMap(c => c.players.map(p => ({ p, c })));
  const snap = x => x ? { name: x.p.name, club: x.c.s, goals: x.p.sg, assists: x.p.sa, age: x.p.age } : null;
  const awards = {
    topScorer: snap(lgPlayers.slice().sort((a, b) => b.p.sg - a.p.sg)[0]),
    bestPlayer: snap(lgPlayers.slice().sort((a, b) => (b.p.sg + b.p.sa) - (a.p.sg + a.p.sa))[0]),
    bestYoung: snap(lgPlayers.filter(x => x.p.age <= 21).sort((a, b) => b.p.ovr - a.p.ovr)[0]),
  };
  // aging, growth, retirement, contracts, youth intake
  for (const c of G.clubs) {
    const country = DB.leagues[c.lg].country;
    for (const p of c.players.slice()) {
      p.age++;
      developPlayer(p);
      p.sg = 0; p.sa = 0; p.apps = 0; p.fit = 100; p.injury = 0;
      p.years--;
      if (p.age >= 35 && Math.random() < (p.age - 34) * 0.35) {
        c.players.splice(c.players.indexOf(p), 1);
        if (c.id === G.userClub || p.ovr >= 84) news(G, `👋 ${p.name} (${p.age}) has retired.`);
        continue;
      }
      if (p.years <= 0) {
        if (c.id !== G.userClub && Math.random() < 0.8) { p.years = 1 + R(3); continue; }
        c.players.splice(c.players.indexOf(p), 1);
        if (c.id === G.userClub) news(G, `📄 ${p.name} left on a free — contract expired.`);
      }
    }
    for (let i = 0; i < 3; i++) c.players.push(genYouth(country));
    c.budget = Math.max(c.budget, initialBudget(c));
    c.morale = 70;
  }
  news(G, `🌱 Youth academy: 3 new prospects joined every academy.`);
  G.season++; G.year++;
  G.time = Date.UTC(G.year, 6, 10);
  genSeason(G);
  const summary = { userPos: G.userPos, prize, champions, proms, awards, board };
  // manager market: bigger clubs come calling when your rep is high
  if (G.rep >= 55 && Math.random() < 0.6) {
    const myPw = power(G.clubs[G.userClub]);
    const cands = G.clubs.filter(x => x.id !== G.userClub && DB.leagues[x.lg].play && power(x) > myPw + 1);
    if (cands.length) summary.jobOffer = pick(cands).id;
  }
  return summary;
}

// ---------- new game ----------
function initialBudget(c) {
  const L = DB.leagues[c.lg];
  const sv = c.players.map(p => p.value).sort((a, b) => b - a).slice(0, 18).reduce((s, v) => s + v, 0);
  const mult = (L.rich ? 2.5 : 1) * (L.name === 'Premier League' ? 1.4 : 1) * (L.level === 2 ? 0.8 : 1);
  return Math.max(2e6, Math.round(sv * 0.12 * mult / 1e5) * 1e5);
}
function newGame(managerName, clubIdx) {
  nextId = 1;
  const G = {
    season: 1, year: 2026, time: Date.UTC(2026, 6, 10),
    managerName, userClub: clubIdx, rep: 30, trophies: [],
    news: [], tx: [], seasonOver: false, pendingOffer: null,
    clubs: DB.clubs.map((c, i) => ({
      id: i, n: c.n, s: c.s, lg: c.lg, c1: c.c1, c2: c.c2, t: c.t || 0,
      morale: 70, mentality: 'balanced',
      formation: i === clubIdx ? '4-3-3' : pick(['4-3-3', '4-4-2', '4-2-3-1', '4-3-2-1', '3-5-2', '5-3-2', '4-1-4-1']),
      buildUp: i === clubIdx ? 'balanced' : pick(['balanced', 'balanced', 'counter', 'slow']),
      defApproach: i === clubIdx ? 'balanced' : pick(['deep', 'balanced', 'balanced', 'high', 'aggressive']),
      width: 'balanced',
      players: c.p.map(row => ({
        id: nextId++, name: row[0], nat: row[1], pos: row[2], age: row[3],
        ovr: row[4], pot: row[5], value: row[6], wage: row[7], years: row[8],
        a: row.slice(9, 15), img: row[15] || null, fit: 100, injury: 0, apps: 0, sg: 0, sa: 0, listed: false,
      })),
    })),
  };
  for (const c of G.clubs) c.budget = initialBudget(c);
  genSeason(G);
  news(G, `👔 ${managerName} appointed manager of ${G.clubs[clubIdx].n}. Welcome!`);
  return G;
}

const ENG = {
  DAY, FORMATIONS, FORMATION_DEF, ROLE_CATALOG, FOCUS_DELTA, KIND_LINE, KIND_LABEL,
  roleStats, defRole, applyFormation, ensureTactics, lineup, teamProfile,
  BUILD, APPR, WIDTHS, newGame, advanceDay, playDay, table, bestXI, power, leagueClubs,
  windowOpen, bid, signPlayer, sellPlayer, completeSale, acceptOffer, endSeason, wageBill,
  genYouth, calcValue, news, boardExpectation, acceptJob,
};
if (typeof module !== 'undefined') module.exports = ENG;
