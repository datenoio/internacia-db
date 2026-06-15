"""Console entry points for internacia_builder."""

from __future__ import annotations

from internacia_builder.validate.countries import app as countries_app
from internacia_builder.validate.intblocks import app as intblocks_app


def validate_countries() -> None:
    countries_app()


def validate_intblocks() -> None:
    intblocks_app()
