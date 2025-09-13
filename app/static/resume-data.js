async function fetchResume() {
  const res = await fetch('/api/resume');
  return await res.json();
}

function formatDate(str) {
  if (!str) return 'Present';
  const [y, m] = str.split('-');
  const d = new Date(Number(y), Number(m) - 1);
  return d.toLocaleString('en-US', { month: 'short', year: 'numeric' });
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
      li.textContent = c.name || c;
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
  contact.innerHTML = `${r.overview.location} | ${r.overview.phone} | <a href="mailto:${r.overview.email}">${r.overview.email}</a> | <a href="${r.overview.web}" target="_blank">${r.overview.web}</a> | <a href="${r.overview.linkedin}" target="_blank">${r.overview.linkedin}</a> | <a href="${r.overview.github}" target="_blank">${r.overview.github}</a>`;
  main.appendChild(contact);

  const expH2 = document.createElement('h2');
  expH2.textContent = 'Professional Experience';
  main.appendChild(expH2);
  r.experience.forEach(exp => {
    const h3 = document.createElement('h3');
    h3.textContent = `${exp.role} – ${exp.company}`;
    main.appendChild(h3);
    const p = document.createElement('p');
    p.textContent = `${formatDate(exp.start)} – ${formatDate(exp.end)} | ${exp.location}`;
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
      li.textContent = c.name || c;
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
