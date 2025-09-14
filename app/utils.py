"""Utility helpers for the resume application.

The original project bundled several helper functions inside ``main.py``.
Moving them into this module keeps the web API focused on routing logic and
provides small, well‑documented helpers that are easier for newcomers to read.
"""

from datetime import datetime
from typing import Optional
import re


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
    year_fmt = f"{int(year):02d}" if short else f"{year}"
    return f"{month:02d}/{day:02d}/{year_fmt}"


def strip_scheme(url: Optional[str]) -> str:
    """Remove the ``http://`` or ``https://`` prefix from ``url``.

    This helper keeps templates concise and avoids repeating string
    manipulation code around the project.
    """
    if not url:
        return ""
    url = re.sub(r"^https?://", "", url, flags=re.IGNORECASE)
    if url.lower().startswith("www."):
        url = url[4:]
    return url

