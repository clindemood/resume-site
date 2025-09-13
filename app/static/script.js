let sessionId; // current CLI session identifier returned by the backend
const terminal = document.getElementById('terminal');
const form = document.getElementById('command-form');
const input = document.getElementById('command');
const history = [];
let historyIndex = -1;

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
    .replace(/https?:\/\/[^\s]+/g, '<span class="link">$&</span>')
    .replace(/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g, '<span class="link">$&</span>')
    .replace(/\[(.*?)\]/g, '<span class="bracket">[$1]</span>')
    .replace(/\b([A-Za-z_]+):/g, '<span class="label">$1:</span>')
    .replace(/\b\d+\b/g, '<span class="number">$&</span>')
    .replace(/\n/g, '<br>');
}

// Append ``text`` to the terminal output area with an optional CSS class
function print(text, cls = 'output') {
  if (text) {
    const line = document.createElement('div');
    line.className = cls;
    if (cls === 'ascii') {
      // Avoid colourisation so spacing is preserved for ASCII art
      line.textContent = text;
    } else {
      line.innerHTML = colorize(text);
    }
    terminal.appendChild(line);
  }
  terminal.scrollTop = terminal.scrollHeight;
}

// Start a new CLI session and show the welcome message
async function start() {
  const res = await fetch('/api/start');
  const data = await res.json();
  sessionId = data.session_id;
  if (data.ascii_art) {
    print(data.ascii_art, 'ascii');
  }
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
  if (Array.isArray(data.lines)) {
    data.lines.forEach((line, idx) => {
      setTimeout(() => print(line, data.error ? 'error' : 'output'), idx * 300);
    });
  } else {
    print(data.text, data.error ? 'error' : 'output');
  }
}

// Handle manual command entry
form.addEventListener('submit', e => {
  e.preventDefault();
  const cmd = input.value;
  input.value = '';
  if (cmd) {
    history.push(cmd);
    historyIndex = history.length;
  }
  sendCommand(cmd);
});

input.addEventListener('keydown', e => {
  if (e.key === 'ArrowUp') {
    if (historyIndex > 0) {
      historyIndex--;
      input.value = history[historyIndex];
    }
    e.preventDefault();
  } else if (e.key === 'ArrowDown') {
    if (historyIndex < history.length - 1) {
      historyIndex++;
      input.value = history[historyIndex];
    } else {
      historyIndex = history.length;
      input.value = '';
    }
    e.preventDefault();
  }
});

// Delegate clicks on the hotkey buttons to send predefined commands
document.getElementById('hotkeys').addEventListener('click', e => {
  if (e.target.dataset.cmd) {
    sendCommand(e.target.dataset.cmd);
  }
});

start();
