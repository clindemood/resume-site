let sessionId; // current CLI session identifier returned by the backend
const terminal = document.getElementById('terminal');
const form = document.getElementById('command-form');
const input = document.getElementById('command');

// Append ``text`` to the terminal output area
function print(text) {
  if (text) {
    terminal.textContent += text + '\n';
  }
  terminal.scrollTop = terminal.scrollHeight;
}

// Start a new CLI session and show the welcome message
async function start() {
  const res = await fetch('/api/start');
  const data = await res.json();
  sessionId = data.session_id;
  print(data.text);
}

// Send a command string to the backend API and render the response
async function sendCommand(cmd) {
  const res = await fetch('/api/command', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, command: cmd })
  });
  const data = await res.json();
  print('> ' + cmd);
  if (data.clear) {
    terminal.textContent = '';
  }
  print(data.text);
}

// Handle manual command entry
form.addEventListener('submit', e => {
  e.preventDefault();
  const cmd = input.value;
  input.value = '';
  sendCommand(cmd);
});

// Delegate clicks on the hotkey buttons to send predefined commands
document.getElementById('hotkeys').addEventListener('click', e => {
  if (e.target.dataset.cmd) {
    sendCommand(e.target.dataset.cmd);
  }
});

start();
