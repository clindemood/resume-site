"""Utility helpers for the resume application.

The original project bundled several helper functions inside ``main.py``.
Moving them into this module keeps the web API focused on routing logic and
provides small, well‑documented helpers that are easier for newcomers to read.
"""

from datetime import datetime
from typing import Optional


def format_date(value: Optional[str], short: bool = False) -> str:
    """Return a human friendly date string.

    Parameters
    ----------
    value:
        A string in ``YYYY-MM`` or ``YYYY-MM-DD`` format.  ``None`` means the
        item is still in progress.
    short:
        When ``True`` the year is rendered with two digits.
    """
    if not value:
        return "Present"

    # ``datetime.strptime`` raises ``ValueError`` if the format does not match,
    # so we try each format in turn.  Using explicit blocks keeps the flow clear
    # for readers who are new to exception handling.
    try:
        dt = datetime.strptime(value, "%Y-%m")
        month, day = dt.month, 1
    except ValueError:
        try:
            dt = datetime.strptime(value, "%Y-%m-%d")
            month, day = dt.month, dt.day
        except ValueError:
            # If the date cannot be parsed we simply return the original text.
            return value

    year = dt.year % 100 if short else dt.year
    return f"{month}/{day}/{year}"


def strip_scheme(url: Optional[str]) -> str:
    """Remove the ``http://`` or ``https://`` prefix from ``url``.

    This helper keeps templates concise and avoids repeating string
    manipulation code around the project.
    """
    if not url:
        return ""
    url = url.replace("https://", "").replace("http://", "")
    if url.startswith("www."):
        url = url[4:]
    return url

