import json
import subprocess
from pathlib import Path


SCRIPT_PATH = Path("app/static/script.js").resolve()


def run_js(function: str, argument: str) -> str:
    js = f"""
const fs=require('fs');
const vm=require('vm');
const path={json.dumps(str(SCRIPT_PATH))};
const script=fs.readFileSync(path,'utf8');
const stub={{
  appendChild: ()=>{{}},
  addEventListener: ()=>{{}},
  scrollTop:0,
  scrollHeight:0,
  textContent:'',
  value:'',
  dataset:{{}}
}};
const document={{
  getElementById: id => stub,
  createElement: tag => ({{...stub}})
}};
const sandbox={{
  console: console,
  document: document,
  window: {{}},
  fetch: () => Promise.resolve({{ json: () => Promise.resolve({{}}) }}),
  setTimeout: () => {{}},
}};
vm.createContext(sandbox);
vm.runInContext(script, sandbox);
const result = sandbox['{function}']({json.dumps(argument)});
if (typeof result === 'string') {{
  console.log(result);
}} else {{
  console.log(JSON.stringify(result));
}}
"""
    completed = subprocess.run(["node", "-e", js], capture_output=True, text=True)
    assert completed.returncode == 0, completed.stderr
    return completed.stdout.strip()


def test_escape_html_strips_tags():
    output = run_js("escapeHtml", "<script>alert('x')</script>")
    assert "<script>" not in output
    assert "&lt;script&gt;" in output


def test_colorize_escapes_html_before_highlighting():
    payload = "<img src=x onerror=alert('xss')>"
    output = run_js("colorize", payload)
    assert "<img" not in output
    assert "&lt;img src=x onerror=alert('xss')&gt;" in output
