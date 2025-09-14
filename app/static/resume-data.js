async function fetchResume() {
  const res = await fetch('/api/resume');
  return await res.json();
}

function stripScheme(url) {
  return url.replace(/^https?:\/\/(www\.)?/, '');
}

function formatDate(str, short = false) {
  if (!str) return 'Present';
  const parts = str.split('-');
  const y = Number(parts[0]);
  const m = Number(parts[1]);
  const d = parts[2] ? Number(parts[2]) : 1;
  const year = short ? String(y).slice(-2) : y;
  return `${m}/${d}/${year}`;
}

function sanitizeText(value) {
  return typeof value === 'string' ? value : String(value ?? '');
}

function sanitizeUrl(url) {
  try {
    const parsed = new URL(String(url), document.baseURI);
    if (parsed.protocol === 'http:' || parsed.protocol === 'https:') {
      return parsed.href;
    }
  } catch {}
  return '#';
}

function sanitizeEmail(email) {
  return encodeURIComponent(sanitizeText(email));
}

export async function loadAbout() {
  const r = await fetchResume();
  const p = document.getElementById('about-text');
  if (p) {
    p.textContent = sanitizeText(r.overview.summary);
  }
}

export async function loadProjects() {
  const r = await fetchResume();
  const list = document.getElementById('projects-list');
  if (list) {
    r.projects.forEach(p => {
      const li = document.createElement('li');
      const heading = document.createElement('strong');
      const start = sanitizeText(p.start);
      const date = start ? `${formatDate(start)} – ` : '';
      heading.textContent = `${date}${sanitizeText(p.name)}`;
      li.appendChild(heading);
      if (Array.isArray(p.bullets) && p.bullets.length) {
        const ul = document.createElement('ul');
        p.bullets.forEach(b => {
          const li2 = document.createElement('li');
          li2.textContent = sanitizeText(b);
          ul.appendChild(li2);
        });
        li.appendChild(ul);
      } else if (p.outcome) {
        const pEl = document.createElement('p');
        pEl.textContent = sanitizeText(p.outcome);
        li.appendChild(pEl);
      }
      list.appendChild(li);
    });
  }
}

export async function loadEducation() {
  const r = await fetchResume();
  const list = document.getElementById('education-list');
  if (list) {
    r.education.forEach(e => {
      const li = document.createElement('li');
      li.textContent = `${sanitizeText(e.institution)} — ${sanitizeText(e.degree)} (${sanitizeText(e.year)})`;
      list.appendChild(li);
    });
  }
  const certList = document.getElementById('certifications-list');
  if (certList && r.certifications) {
    r.certifications.forEach(c => {
      const li = document.createElement('li');
      li.textContent = sanitizeText(c.name);
      certList.appendChild(li);
    });
  }
}

export async function loadResume() {
  const r = await fetchResume();
  const main = document.getElementById('resume-container');
  if (!main) return;

  const h1 = document.createElement('h1');
  h1.textContent = sanitizeText(r.overview.name);
  main.appendChild(h1);

  const contact = document.createElement('p');
  const addPart = content => {
    if (contact.childNodes.length) {
      contact.appendChild(document.createTextNode(' | '));
    }
    if (typeof content === 'string') {
      contact.appendChild(document.createTextNode(content));
    } else {
      contact.appendChild(content);
    }
  };
  addPart(sanitizeText(r.overview.location));
  if (r.overview.email) {
    const a = document.createElement('a');
    a.href = `mailto:${sanitizeEmail(r.overview.email)}`;
    a.textContent = sanitizeText(r.overview.email);
    addPart(a);
  }
  if (r.overview.web) {
    const a = document.createElement('a');
    a.href = sanitizeUrl(r.overview.web);
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    a.textContent = stripScheme(a.href);
    addPart(a);
  }
  if (r.overview.linkedin) {
    const a = document.createElement('a');
    a.href = sanitizeUrl(r.overview.linkedin);
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    a.textContent = 'LinkedIn';
    addPart(a);
  }
  if (r.overview.github) {
    const a = document.createElement('a');
    a.href = sanitizeUrl(r.overview.github);
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    a.textContent = 'GitHub';
    addPart(a);
  }
  main.appendChild(contact);

  const expH2 = document.createElement('h2');
  expH2.textContent = 'Professional Experience';
  main.appendChild(expH2);
  r.experience.forEach(exp => {
    const h3 = document.createElement('h3');
    h3.textContent = `${sanitizeText(exp.role)} – ${sanitizeText(exp.company)}`;
    main.appendChild(h3);
    const p = document.createElement('p');
    const start = sanitizeText(exp.start);
    const end = sanitizeText(exp.end);
    p.textContent = `${formatDate(start)} - ${formatDate(end, true)} | ${sanitizeText(exp.location)}`;
    main.appendChild(p);
    if (exp.bullets && exp.bullets.length) {
      const ul = document.createElement('ul');
      exp.bullets.forEach(b => {
        const li = document.createElement('li');
        li.textContent = sanitizeText(b);
        ul.appendChild(li);
      });
      main.appendChild(ul);
    }
  });

  const eduH2 = document.createElement('h2');
  eduH2.textContent = 'Education';
  main.appendChild(eduH2);
  const eduUl = document.createElement('ul');
  r.education.forEach(e => {
    const li = document.createElement('li');
    li.textContent = `${sanitizeText(e.institution)} – ${sanitizeText(e.degree)} (${sanitizeText(e.year)})`;
    eduUl.appendChild(li);
  });
  main.appendChild(eduUl);

  if (r.certifications && r.certifications.length) {
    const certH2 = document.createElement('h2');
    certH2.textContent = 'Certifications';
    main.appendChild(certH2);
    const certUl = document.createElement('ul');
    r.certifications.forEach(c => {
      const li = document.createElement('li');
      const details = [];
      if (c.issuer) details.push(sanitizeText(c.issuer));
      if (c.credential_id) details.push(`ID ${sanitizeText(c.credential_id)}`);
      li.textContent = details.length ? `${sanitizeText(c.name)} — ${details.join(' · ')}` : sanitizeText(c.name);
      certUl.appendChild(li);
    });
    main.appendChild(certUl);
  }

  const skillH2 = document.createElement('h2');
  skillH2.textContent = 'Technical Skills';
  main.appendChild(skillH2);
  const skillUl = document.createElement('ul');
  const categories = { cloud: [], endpoint: [], network: [], collaboration: [] };
  r.skills.forEach(s => {
    if (Array.isArray(s.tags)) {
      s.tags.forEach(tag => {
        if (categories[tag]) {
          categories[tag].push(sanitizeText(s.name));
        }
      });
    }
  });
  const labels = {
    cloud: 'Cloud & Systems',
    endpoint: 'Endpoint Management',
    network: 'Networking & Security',
    collaboration: 'Collaboration Tools'
  };
  Object.entries(labels).forEach(([tag, label]) => {
    const names = categories[tag];
    if (names.length) {
      const li = document.createElement('li');
      li.textContent = `${label}: ${names.join(', ')}`;
      skillUl.appendChild(li);
    }
  });
  main.appendChild(skillUl);
}
