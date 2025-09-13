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

export async function loadAbout() {
  const r = await fetchResume();
  const p = document.getElementById('about-text');
  if (p) {
    p.textContent = r.overview.summary;
  }
}

export async function loadProjects() {
  const r = await fetchResume();
  const list = document.getElementById('projects-list');
  if (list) {
    r.projects.forEach(p => {
      const li = document.createElement('li');
      li.textContent = p.outcome ? `${p.name} — ${p.outcome}` : p.name;
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
      li.textContent = `${e.institution} — ${e.degree} (${e.year})`;
      list.appendChild(li);
    });
  }
  const certList = document.getElementById('certifications-list');
  if (certList && r.certifications) {
    r.certifications.forEach(c => {
      const li = document.createElement('li');
      li.textContent = c.name;
      certList.appendChild(li);
    });
  }
}

export async function loadResume() {
  const r = await fetchResume();
  const main = document.getElementById('resume-container');
  if (!main) return;

  const h1 = document.createElement('h1');
  h1.textContent = r.overview.name;
  main.appendChild(h1);

  const contact = document.createElement('p');
  const parts = [
    r.overview.location,
    `<a href="mailto:${r.overview.email}">${r.overview.email}</a>`,
    `<a href="${r.overview.web}" target="_blank">${stripScheme(r.overview.web)}</a>`,
    `<a href="${r.overview.linkedin}" target="_blank">LinkedIn</a>`,
    `<a href="${r.overview.github}" target="_blank">GitHub</a>`
  ];
  contact.innerHTML = parts.join(' | ');
  main.appendChild(contact);

  const expH2 = document.createElement('h2');
  expH2.textContent = 'Professional Experience';
  main.appendChild(expH2);
  r.experience.forEach(exp => {
    const h3 = document.createElement('h3');
    h3.textContent = `${exp.role} – ${exp.company}`;
    main.appendChild(h3);
    const p = document.createElement('p');
    p.textContent = `${formatDate(exp.start)} - ${formatDate(exp.end, true)} | ${exp.location}`;
    main.appendChild(p);
    if (exp.bullets && exp.bullets.length) {
      const ul = document.createElement('ul');
      exp.bullets.forEach(b => {
        const li = document.createElement('li');
        li.textContent = b;
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
    li.textContent = `${e.institution} – ${e.degree} (${e.year})`;
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
      if (c.issuer) details.push(c.issuer);
      if (c.credential_id) details.push(`ID ${c.credential_id}`);
      li.textContent = details.length ? `${c.name} — ${details.join(' · ')}` : c.name;
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
          categories[tag].push(s.name);
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
