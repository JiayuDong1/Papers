const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  selectInputFile: () => ipcRenderer.invoke('select-input-file'),
  startBackendJob: (job) => ipcRenderer.invoke('start-backend-job', job),
  onBackendLog: (cb) => ipcRenderer.on('backend-log', (_e, text) => cb(text)),
  onBackendExit: (cb) => ipcRenderer.on('backend-exit', (_e, code) => cb(code)),
});
