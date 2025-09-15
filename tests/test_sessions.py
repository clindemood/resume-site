import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.main import SESSION_TTL, prune_sessions, sessions


def test_prune_sessions_respects_ttl():
    """Sessions younger than the TTL should not be removed."""

    sessions.clear()

    # Session older than the TTL should be pruned.
    old_id = "old"
    sessions[old_id] = {"_ts": time.time() - (SESSION_TTL + 1)}

    # Session within the TTL should remain.
    young_id = "young"
    sessions[young_id] = {"_ts": time.time() - (SESSION_TTL - 1)}

    prune_sessions(now=time.time())

    assert old_id not in sessions
    assert young_id in sessions

