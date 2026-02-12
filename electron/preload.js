const { contextBridge } = require('electron');

// Expose safe APIs to the renderer process
contextBridge.exposeInMainWorld('electronAPI', {
  // Add backend communication APIs here if needed
});

// Log when preload is executed
console.log('Preload script loaded');
