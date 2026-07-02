// Desktop app wrapper (Electron). Run: npm install electron --save-dev && npm start
const { app, BrowserWindow } = require('electron');
app.whenReady().then(() => {
  const win = new BrowserWindow({ width: 1280, height: 800, autoHideMenuBar: true, title: 'Locking In FC', backgroundColor: '#05070c' });
  win.loadFile('index.html');
});
app.on('window-all-closed', () => app.quit());
