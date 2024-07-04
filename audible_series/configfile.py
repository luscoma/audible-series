from collections import namedtuple

from yaml import safe_load


class ConfigData(
        namedtuple('ConfigData', [
            # A set of series titles to skip
            'series_to_skip',
            # ASINs of books already preordered
            'preordered_asins',
            # A mapping of series title: asin that is used to override the
            # latest book for a series (useful if a later book was read on
            # kindle or elsewhere)
            'external_library',
            # ASINs that should not be considered the next in a series or in the
            # library.  This is useful for ongoing series where Audible puts a
            # spin-off or short story after the latest entry in the series.
            'disallowed_asins'
        ])):

    @classmethod
    def from_yaml(cls, data):
        if not data:  # Can happen if yaml is empty
            data = {}
        skipped = data.get('series_to_skip', [])
        preordered = data.get('preordered_asin', [])
        external_library = data.get('external_library', {})
        disallowed = data.get('disallowed_asins', [])
        return cls(
            frozenset(skipped),
            frozenset(preordered),
            external_library,
            frozenset(disallowed)
        )

    @classmethod
    def empty(cls):
        return cls(frozenset(), frozenset(), {}, frozenset())


def load(config_file):
    if not config_file:
        return ConfigData.empty()

    with open(config_file) as f:
        data = safe_load(f)

    return ConfigData.from_yaml(data)
