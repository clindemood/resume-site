const terminal = document.getElementById('terminal');
const form = document.getElementById('command-form');
const input = document.getElementById('command');

function print(text) {
  terminal.textContent += text + '\n';
  terminal.scrollTop = terminal.scrollHeight;
}

async function loadSection(section) {
  try {
    const res = await fetch('/' + section);
    const html = await res.text();
    const doc = new DOMParser().parseFromString(html, 'text/html');
    const main = doc.querySelector('main');
    const text = main ? main.textContent.trim() : 'Section not found.';
    print(text);
  } catch (err) {
    print('Error loading section.');
  }
}

const commands = {
  help() {
    print('Available commands: about, projects, education, resume, clear, help');
  },
  clear() {
    terminal.textContent = '';
  },
  about: () => loadSection('about'),
  projects: () => loadSection('projects'),
  education: () => loadSection('education'),
  resume: () => loadSection('resume')
};

print("Welcome to Chad Lindemood's CLI resume. Type 'help' for commands.");

form.addEventListener('submit', e => {
  e.preventDefault();
  const cmd = input.value.trim().toLowerCase();
  input.value = '';
  if (!cmd) return;
  print('$ ' + cmd);
  const action = commands[cmd];
  if (action) {
    action();
  } else {
    print('Unknown command. Type "help" for available commands.');
  }
});
