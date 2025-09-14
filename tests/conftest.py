import sys
from pathlib import Path

# Ensure project root is on sys.path so that `import app` works when tests
# are executed from a different working directory or when Python does not
# automatically include the current directory on the module search path.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
