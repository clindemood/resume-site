let sessionId;
const terminal = document.getElementById('terminal');
const form = document.getElementById('command-form');
const input = document.getElementById('command');

function print(text) {
  terminal.textContent += text + '\n';
  terminal.scrollTop = terminal.scrollHeight;
}

async function start() {
  const res = await fetch('/api/start');
  const data = await res.json();
  sessionId = data.session_id;
  print(data.text);
}

async function sendCommand(cmd) {
  const res = await fetch('/api/command', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, command: cmd })
  });
  const data = await res.json();
  print('> ' + cmd);
  print(data.text);
}

form.addEventListener('submit', e => {
  e.preventDefault();
  const cmd = input.value;
  input.value = '';
  sendCommand(cmd);
});

document.getElementById('hotkeys').addEventListener('click', e => {
  if (e.target.dataset.cmd) {
    sendCommand(e.target.dataset.cmd);
  }
});

start();
