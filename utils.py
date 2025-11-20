"""Utility helpers for the Intelar scale integration."""
from __future__ import annotations

import logging
from datetime import date, datetime

_LOGGER = logging.getLogger(__name__)


def calculate_age_from_birthdate(birthdate_str: str) -> int:
    """Calculate current age from birthdate string in YYYY-MM-DD format."""

    try:
        birth_date = datetime.strptime(birthdate_str, "%Y-%m-%d").date()
        today = date.today()
        return today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )
    except (ValueError, TypeError):
        _LOGGER.warning("Invalid birthdate format: %s, using default age 30", birthdate_str)
        return 30
