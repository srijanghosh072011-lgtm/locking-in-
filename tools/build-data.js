// tools/build-data.js — converts the FC26 sofifa CSV dump into data.js for the game.
// Usage: node tools/build-data.js path/to/FC26_Dataset.csv
'use strict';
const fs = require('fs');

const csvPath = process.argv[2];
if (!csvPath) { console.error('usage: node tools/build-data.js FC26_Dataset.csv'); process.exit(1); }

function parseCSV(text) {
  const rows = []; let row = [], cur = '', q = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (q) { if (ch === '"') { if (text[i + 1] === '"') { cur += '"'; i++; } else q = false; } else cur += ch; }
    else if (ch === '"') q = true;
    else if (ch === ',') { row.push(cur); cur = ''; }
    else if (ch === '\n') { row.push(cur); rows.push(row); row = []; cur = ''; }
    else if (ch !== '\r') cur += ch;
  }
  if (cur || row.length) { row.push(cur); rows.push(row); }
  return rows;
}

// leagues: D1 picked by EA league_id (names collide across countries), D2 by unique name+level
const LEAGUES = [
  { eaId: 13, name: 'Premier League', country: 'England', flag: '🏴󠁧󠁢󠁥󠁮󠁧󠁿', level: 1, play: 1, uefa: 1, d2: 6 },
  { eaId: 53, name: 'La Liga', country: 'Spain', flag: '🇪🇸', level: 1, play: 1, uefa: 1, d2: 7 },
  { eaId: 19, name: 'Bundesliga', country: 'Germany', flag: '🇩🇪', level: 1, play: 1, uefa: 1, d2: 8 },
  { eaId: 31, name: 'Serie A', country: 'Italy', flag: '🇮🇹', level: 1, play: 1, uefa: 1, d2: 9 },
  { eaId: 16, name: 'Ligue 1', country: 'France', flag: '🇫🇷', level: 1, play: 1, uefa: 1, d2: 10 },
  { eaId: 308, name: 'Primeira Liga', country: 'Portugal', flag: '🇵🇹', level: 1, play: 1, uefa: 1, d2: null },
  { key: 'Championship|2', name: 'Championship', country: 'England', flag: '🏴󠁧󠁢󠁥󠁮󠁧󠁿', level: 2, play: 1 },
  { key: 'La Liga 2|2', name: 'La Liga 2', country: 'Spain', flag: '🇪🇸', level: 2, play: 1 },
  { key: '2. Bundesliga|2', name: '2. Bundesliga', country: 'Germany', flag: '🇩🇪', level: 2, play: 1 },
  { key: 'Serie B|2', name: 'Serie B', country: 'Italy', flag: '🇮🇹', level: 2, play: 1 },
  { key: 'Ligue 2|2', name: 'Ligue 2', country: 'France', flag: '🇫🇷', level: 2, play: 1 },
  { eaId: 350, name: 'Saudi Pro League', country: 'Saudi Arabia', flag: '🇸🇦', level: 1, play: 0, rich: 3 },
  { eaId: 39, name: 'MLS', country: 'USA', flag: '🇺🇸', level: 1, play: 0 },
  { eaId: 68, name: 'Süper Lig', country: 'Türkiye', flag: '🇹🇷', level: 1, play: 0, uefa: 1 },
];

// hand colors [primary, secondary, short?] for famous clubs; everyone else gets hashed colors
const COLORS = {
  'Liverpool': ['#c8102e', '#f6eb61', 'LIV'], 'Manchester City': ['#6caddf', '#1c2c5b', 'MCI'],
  'Manchester United': ['#da291c', '#fbe122', 'MUN'], 'Arsenal': ['#ef0107', '#ffffff', 'ARS'],
  'Chelsea': ['#034694', '#ffffff', 'CHE'], 'Tottenham Hotspur': ['#132257', '#ffffff', 'TOT'],
  'Newcastle United': ['#241f20', '#ffffff', 'NEW'], 'Aston Villa': ['#670e36', '#95bfe5', 'AVL'],
  'West Ham United': ['#7a263a', '#1bb1e7', 'WHU'], 'Everton': ['#003399', '#ffffff', 'EVE'],
  'Brighton & Hove Albion': ['#0057b8', '#ffffff', 'BHA'], 'Crystal Palace': ['#1b458f', '#c4122e', 'CRY'],
  'Real Madrid': ['#febe10', '#00529f', 'RMA'], 'FC Barcelona': ['#a50044', '#004d98', 'BAR'],
  'Atlético Madrid': ['#cb3524', '#ffffff', 'ATM'], 'Sevilla FC': ['#d8091f', '#ffffff', 'SEV'],
  'Real Betis': ['#00954c', '#ffffff', 'BET'], 'Real Sociedad': ['#0067b1', '#ffffff', 'RSO'],
  'Athletic Club': ['#ee2523', '#ffffff', 'ATH'], 'Villarreal CF': ['#ffe667', '#005187', 'VIL'],
  'Valencia CF': ['#f7b800', '#000000', 'VAL'],
  'FC Bayern München': ['#dc052d', '#ffffff', 'FCB'], 'Borussia Dortmund': ['#fde100', '#000000', 'BVB'],
  'Bayer 04 Leverkusen': ['#e32221', '#000000', 'B04'], 'RB Leipzig': ['#dd0741', '#ffffff', 'RBL'],
  'Eintracht Frankfurt': ['#e1000f', '#000000', 'SGE'], 'VfB Stuttgart': ['#e32219', '#ffffff', 'VFB'],
  'Borussia Mönchengladbach': ['#000000', '#ffffff', 'BMG'],
  'Inter': ['#0068a8', '#221f20', 'INT'], 'AC Milan': ['#fb090b', '#000000', 'MIL'],
  'Juventus': ['#000000', '#ffffff', 'JUV'], 'Napoli': ['#12a0d7', '#ffffff', 'NAP'],
  'AS Roma': ['#8e1f2f', '#f0bc42', 'ROM'], 'Lazio': ['#87d8f7', '#ffffff', 'LAZ'],
  'Atalanta': ['#1e71b8', '#000000', 'ATA'], 'Fiorentina': ['#582c83', '#ffffff', 'FIO'],
  'Paris Saint-Germain': ['#004170', '#da291c', 'PSG'], 'Olympique de Marseille': ['#2faee0', '#ffffff', 'OM'],
  'Olympique Lyonnais': ['#da001a', '#1a2e5a', 'OL'], 'AS Monaco': ['#e63031', '#ffffff', 'ASM'],
  'LOSC Lille': ['#e01e13', '#233d7b', 'LIL'],
  'SL Benfica': ['#e83030', '#ffffff', 'SLB'], 'FC Porto': ['#00428c', '#ffffff', 'POR'],
  'Sporting CP': ['#008057', '#ffffff', 'SCP'], 'Sporting Clube de Braga': ['#d01e25', '#ffffff', 'BRA'],
  'Al Hilal': ['#0000ff', '#ffffff', 'HIL'], 'Al Nassr': ['#ffd700', '#00308f', 'NAS'],
  'Al Ahli SFC': ['#00733b', '#ffffff', 'AHL'], 'Al Ittihad': ['#f9d616', '#000000', 'ITT'],
  'Inter Miami': ['#f7b5cd', '#231f20', 'MIA'], 'LA Galaxy': ['#00245d', '#ffd200', 'LAG'],
  'Los Angeles FC': ['#000000', '#c39e6d', 'LFC'],
  'Galatasaray SK': ['#a90432', '#fdb912', 'GAL'], 'Fenerbahçe SK': ['#163962', '#ffed00', 'FEN'],
  'Beşiktaş JK': ['#000000', '#ffffff', 'BJK'], 'Trabzonspor': ['#841e3d', '#5ec3e8', 'TRA'],
  'Leeds United': ['#ffffff', '#1d428a', 'LEE'], 'Sunderland': ['#eb172b', '#ffffff', 'SUN'],
};

function hashColor(name) {
  let h = 0;
  for (const ch of name) h = (h * 31 + ch.codePointAt(0)) >>> 0;
  return ['hsl(' + h % 360 + ',60%,42%)', h % 2 ? '#f2f2f2' : '#101820'];
}
function shortCode(name) {
  const words = name.replace(/\b(FC|CF|SC|SK|JK|AS|SS|AC|CD|UD|SD|RC|SL|VfL|VfB|TSG|SV|1\.|04|05|09)\b\.?/g, '').trim().split(/\s+/);
  const s = words.length >= 2 ? words.map(w => w[0]).join('').slice(0, 3) : words[0].slice(0, 3);
  return s.toUpperCase().replace(/[^A-ZÀ-Þ]/g, '').slice(0, 3) || name.slice(0, 3).toUpperCase();
}
const POS = s => { const p = s.split(',')[0].trim(); return p === 'GK' ? 'GK' : ['CB', 'LB', 'RB', 'LWB', 'RWB'].includes(p) ? 'DF' : ['CDM', 'CM', 'CAM', 'LM', 'RM'].includes(p) ? 'MF' : 'AT'; };
const fallbackValue = (ovr, age) => Math.max(100e3, Math.round(Math.pow(Math.max(1, ovr - 55), 2.9) * 3000 * (age <= 23 ? 1.3 : age <= 30 ? 1 : 0.4) / 1e5) * 1e5);

const rows = parseCSV(fs.readFileSync(csvPath, 'utf8'));
const H = rows[0], col = {}; H.forEach((h, i) => col[h] = i);
const g = (r, name) => r[col[name]];

const clubs = new Map(); // clubName -> {n,s,lg,c1,c2,p:[]}
let kept = 0;
for (const r of rows.slice(1)) {
  const eaId = +g(r, 'league_id'), lname = g(r, 'league_name'), level = g(r, 'league_level');
  const li = LEAGUES.findIndex(L => L.eaId ? L.eaId === eaId : L.key === lname + '|' + level);
  if (li < 0) continue;
  const clubName = g(r, 'club_name');
  if (!clubName) continue;
  if (!clubs.has(clubName)) {
    const [c1, c2, s] = COLORS[clubName] || [...hashColor(clubName), null];
    clubs.set(clubName, { n: clubName, s: s || shortCode(clubName), lg: li, c1, c2, p: [] });
  }
  const ovr = +g(r, 'overall'), age = +g(r, 'age'), pos = POS(g(r, 'player_positions'));
  const num = (name, fb) => { const v = +g(r, name); return Number.isFinite(v) && v > 0 ? v : fb; };
  const attrs = pos === 'GK'
    ? ['goalkeeping_diving', 'goalkeeping_handling', 'goalkeeping_kicking', 'goalkeeping_reflexes', 'goalkeeping_speed', 'goalkeeping_positioning'].map(a => num(a, 50))
    : ['pace', 'shooting', 'passing', 'dribbling', 'defending', 'physic'].map(a => num(a, 50));
  const until = +g(r, 'club_contract_valid_until_year');
  clubs.get(clubName).p.push([
    g(r, 'short_name'), g(r, 'nationality_name'), pos, age, ovr,
    Math.max(ovr, +g(r, 'potential') || ovr),
    num('value_eur', fallbackValue(ovr, age)),
    num('wage_eur', 5000),
    Math.min(6, Math.max(1, (until || 2028) - 2026)),
    ...attrs,
  ]);
  kept++;
}

const data = {
  source: 'EA Sports FC 26 (sofifa dump, update 4, Sep 2025)',
  // player row: [name, nat, pos, age, ovr, pot, value€, wage€/wk, contractYears, a1..a6]
  // a1..a6 = pac/sho/pas/dri/def/phy for outfield, div/han/kic/ref/spe/pos for GK
  leagues: LEAGUES.map(({ name, country, flag, level, play, uefa, rich, d2 }) => ({ name, country, flag, level, play: !!play, uefa: !!uefa, rich: rich || 0, d2: d2 ?? null })),
  clubs: [...clubs.values()].sort((a, b) => a.lg - b.lg),
};
for (const [i, L] of data.leagues.entries()) {
  const n = data.clubs.filter(c => c.lg === i).length;
  console.log(`${L.flag} ${L.name}: ${n} clubs`);
  if (n < 12) throw new Error('league looks broken: ' + L.name);
}
fs.writeFileSync(__dirname + '/../data.js',
  '// generated by tools/build-data.js — do not edit\nconst DATA = ' + JSON.stringify(data) + ';\nif (typeof module !== "undefined") module.exports = DATA;\n');
console.log(`wrote data.js: ${data.clubs.length} clubs, ${kept} players`);
