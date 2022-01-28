__version__ = "0.0.0"

CONTENT = (
    "karma",
    "karma-given",
    "karma-taken",
    "points",
    "hug",
    "pet",
    "hyperpet",
    "lick",
    "hyperlick",
    "spank",
)


def comma_separated_content() -> str:
    return ", ".join(f"'{c}'" for c in CONTENT)
