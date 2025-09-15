(function () {
  const storageKey = 'preferred-theme';
  const toggle = document.getElementById('theme-toggle');
  const body = document.body;

  if (!toggle || !body) {
    return;
  }

  const icon = toggle.querySelector('.theme-toggle__icon');
  const text = toggle.querySelector('.theme-toggle__text');
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

  const readStoredTheme = () => {
    try {
      return localStorage.getItem(storageKey);
    } catch (err) {
      return null;
    }
  };

  const storeTheme = theme => {
    try {
      localStorage.setItem(storageKey, theme);
    } catch (err) {
      /* ignore write errors */
    }
  };

  const updateToggleContent = theme => {
    if (icon) {
      icon.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
    if (text) {
      text.textContent = theme === 'dark' ? 'Light' : 'Dark';
    }
    toggle.setAttribute('aria-label', theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme');
    toggle.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
  };

  const applyTheme = theme => {
    const normalized = theme === 'dark' ? 'dark' : 'light';
    body.classList.remove('light-theme', 'dark-theme');
    body.classList.add(`${normalized}-theme`);
    updateToggleContent(normalized);
  };

  const getPreferredTheme = () => {
    const stored = readStoredTheme();
    if (stored === 'light' || stored === 'dark') {
      return stored;
    }
    return mediaQuery.matches ? 'dark' : 'light';
  };

  applyTheme(getPreferredTheme());

  toggle.addEventListener('click', () => {
    const isDark = body.classList.contains('dark-theme');
    const nextTheme = isDark ? 'light' : 'dark';
    applyTheme(nextTheme);
    storeTheme(nextTheme);
  });

  const handlePreferenceChange = event => {
    if (readStoredTheme()) {
      return;
    }
    applyTheme(event.matches ? 'dark' : 'light');
  };

  if (typeof mediaQuery.addEventListener === 'function') {
    mediaQuery.addEventListener('change', handlePreferenceChange);
  } else if (typeof mediaQuery.addListener === 'function') {
    mediaQuery.addListener(handlePreferenceChange);
  }
})();
