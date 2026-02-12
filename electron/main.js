const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

let mainWindow = null;
let backendProcess = null;

const isDev = process.env.NODE_ENV === 'development';
const BACKEND_PORT = 8000;

function getResourcePath(relativePath) {
  if (isDev) {
    return path.join(__dirname, '..', relativePath);
  }
  return path.join(process.resourcesPath, relativePath);
}

function getPythonCommand() {
  // Check for virtual environment first
  const venvPython = path.join(getResourcePath('app'), '..', '.venv', 'bin', 'python');
  if (fs.existsSync(venvPython)) {
    return venvPython;
  }

  // Fallback to system Python
  return process.platform === 'win32' ? 'python' : 'python3';
}

// Check if a port is in use
const net = require('net');

function checkPort(port, timeout = 1000) {
  return new Promise((resolve) => {
    const socket = new net.Socket();
    const onError = () => {
      socket.destroy();
      resolve(false);
    };

    socket.setTimeout(timeout);
    socket.once('error', onError);
    socket.once('timeout', onError);

    socket.connect(port, '127.0.0.1', () => {
      socket.end();
      resolve(true);
    });
  });
}


async function startBackend() {
  const isRunning = await checkPort(BACKEND_PORT);
  if (isRunning) {
    console.log(`Backend already running on port ${BACKEND_PORT}, skipping spawn.`);
    return;
  }

  return new Promise((resolve, reject) => {
    console.log('Starting Python backend...');
    const pythonCmd = getPythonCommand();
    const appPath = getResourcePath('app');

    backendProcess = spawn(pythonCmd, [
      '-m', 'uvicorn',
      'app.backend.main:app',
      '--host', '127.0.0.1',
      '--port', String(BACKEND_PORT),
      '--reload'
    ], {
      cwd: path.join(appPath, '..'),
      env: { ...process.env, PYTHONPATH: path.join(appPath, '..') },
      stdio: ['pipe', 'pipe', 'pipe']
    });

    const onData = (data) => {
      const output = data.toString();
      console.log(`[Backend] ${output.trim()}`);
      if (output.includes('Uvicorn running') ||
          output.includes('Application startup complete') ||
          output.includes('Application ready')) {
        resolve();
      }
    };

    backendProcess.stdout.on('data', onData);
    backendProcess.stderr.on('data', (data) => {
      const output = data.toString();
      console.error(`[Backend Error] ${output.trim()}`);
      if (output.includes('Uvicorn running') ||
          output.includes('Application startup complete')) {
        resolve();
      }
    });

    backendProcess.on('error', (err) => {
      console.error('Failed to start backend:', err);
      reject(err);
    });

    // Fallback timeout
    setTimeout(resolve, 15000);
  });
}

function stopBackend() {
  if (backendProcess) {
    console.log('Stopping backend...');
    if (process.platform === 'win32') {
      spawn('taskkill', ['/pid', backendProcess.pid, '/f', '/t']);
    } else {
      backendProcess.kill('SIGTERM');
    }
    backendProcess = null;
  }
}

async function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200, height: 800, minWidth: 800, minHeight: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
    titleBarStyle: 'default',
    show: false,
    icon: path.join(__dirname, 'resources', 'icon.png')
  });

  mainWindow.once('ready-to-show', () => mainWindow.show());

  if (isDev) {
    const frontendPort = process.env.FRONTEND_PORT || 5173;
    const devUrl = `http://localhost:${frontendPort}`;
    console.log(`Waiting for frontend to be ready on port ${frontendPort}...`);

    let ready = false;
    for (let i = 0; i < 10; i++) {
      ready = await checkPort(frontendPort, 1000);
      if (ready) break;
      await new Promise(r => setTimeout(r, 1000));
    }

    if (ready) {
      mainWindow.loadURL(devUrl);
      mainWindow.webContents.openDevTools();
    } else {
      console.error('Frontend port check failed, trying to load anyway...');
      mainWindow.loadURL(devUrl);
      mainWindow.webContents.openDevTools();
    }
  } else {
    mainWindow.loadURL(`http://localhost:${BACKEND_PORT}`);
  }

  mainWindow.on('closed', () => (mainWindow = null));
}

// App lifecycle
app.whenReady().then(async () => {
  try {
    // Start backend first
    await startBackend();
    console.log('Backend started successfully');

    // Then create window
    await createWindow();
  } catch (error) {
    console.error('Failed to start application:', error);
    dialog.showErrorBox('Startup Error',
      'Failed to start the application. Please ensure Python is installed and try again.');
    app.quit();
  }

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  stopBackend();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  stopBackend();
});
