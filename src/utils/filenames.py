from pathlib import Path


def collect_new_name(new_stem: str, old_filename: str) -> str:
    """
    Collect new filename with the new stem and
    original extension.
    """
    suffix = Path(old_filename).suffix
    new_stem += suffix
    return new_stem
