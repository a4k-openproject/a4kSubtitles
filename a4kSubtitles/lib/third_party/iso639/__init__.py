from typing import Iterator

from .datafile import load_langs
from .iso639 import Lang

Lang = Lang


def iter_langs() -> Iterator[Lang]:
    """Iterate through all not deprecated ISO 639 languages

    Yields
    -------
    Lang
        Lang instances ordered alphabetically by name
    """
    sorted_langs = load_langs()

    return iter(sorted_langs)
