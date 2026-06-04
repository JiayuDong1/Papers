const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const log = require('electron-log');
const { spawn } = require('child_process');

let mainWindow;
let backendProc;

function getBackendCwd() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, 'backend');
  }
  return path.join(__dirname, '../../../backend');
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1100,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, '../preload/preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    }
  });

  mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});

ipcMain.handle('select-input-file', async () => {
  const res = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [
      { name: 'Word/Excel', extensions: ['docx', 'xlsx'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });
  if (res.canceled || !res.filePaths?.length) return null;
  return res.filePaths[0];
});

ipcMain.handle('start-backend-job', async (_event, job) => {
  // job: { inputFile, pastedText, outputRoot, proxy, resume }
  // Placeholder backend invocation. Implemented once backend API is ready.

  if (backendProc) {
    try { backendProc.kill(); } catch (_) {}
    backendProc = null;
  }

  const backendExe = 'python';
  const args = [
    '-m', 'oa_downloader',
    '--output-root', job.outputRoot || 'D:\\Papers',
    '--delay-seconds', '1',
    '--retries', '3',
    '--timeout-seconds', '30',
  ];

  if (job.inputFile) args.push('--input-file', job.inputFile);
  if (job.pastedText) args.push('--pasted-text', job.pastedText);
  if (job.proxy) args.push('--proxy', job.proxy);
  if (job.resume) args.push('--resume');

  log.info('Starting backend:', backendExe, args.join(' '));

  backendProc = spawn(backendExe, args, {
    cwd: getBackendCwd(),
    windowsHide: true,
  });

  backendProc.stdout.on('data', (data) => {
    const text = data.toString();
    mainWindow.webContents.send('backend-log', text);
  });

  backendProc.stderr.on('data', (data) => {
    const text = data.toString();
    mainWindow.webContents.send('backend-log', text);
  });

  backendProc.on('exit', (code) => {
    mainWindow.webContents.send('backend-exit', code);
    backendProc = null;
  });

  return true;
});
