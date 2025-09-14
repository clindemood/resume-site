async function loadNav() {
  const res = await fetch('/static/nav.html');
  document.getElementById('site-nav').innerHTML = await res.text();
}

loadNav();

