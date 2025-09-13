let sessionId; // current CLI session identifier returned by the backend
const terminal = document.getElementById('terminal');
const form = document.getElementById('command-form');
const input = document.getElementById('command');

// Escape HTML special characters so user content cannot inject markup
function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

// Add simple syntax highlighting to imitate IDE colour schemes
function colorize(text) {
  return escapeHtml(text)
    .replace(/\[(.*?)\]/g, '<span class="bracket">[$1]</span>')
    .replace(/\b([A-Za-z_]+):/g, '<span class="label">$1:</span>')
    .replace(/\b\d+\b/g, '<span class="number">$&</span>')
    .replace(/https?:\/\/[^\s]+/g, '<span class="link">$&</span>')
    .replace(/\n/g, '<br>');
}

// Append ``text`` to the terminal output area with an optional CSS class
function print(text, cls = 'output') {
  if (text) {
    const line = document.createElement('div');
    line.className = cls;
    line.innerHTML = colorize(text);
    terminal.appendChild(line);
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
  print('$ ' + cmd, 'input');
  if (data.clear) {
    terminal.textContent = '';
  }
  print(data.text, data.error ? 'error' : 'output');
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
