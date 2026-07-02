// tools/bundle.js — inlines data.js + engine.js into index.html → LockingInFC.html (single-file game)
'use strict';
const fs = require('fs');
const root = __dirname + '/..';
const html = fs.readFileSync(root + '/index.html', 'utf8');
const inline = f => '<script>\n' + fs.readFileSync(root + '/' + f, 'utf8') + '\n</script>';
const out = html
  .replace('<script src="data.js"></script>', () => inline('data.js'))
  .replace('<script src="engine.js"></script>', () => inline('engine.js'));
if (out === html) throw new Error('script tags not found');
fs.writeFileSync(root + '/LockingInFC.html', out);
console.log('wrote LockingInFC.html:', (out.length / 1e6).toFixed(2) + 'MB — one file, works anywhere');
