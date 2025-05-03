import pickle
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def load_pickle_file(filepath: Path) -> object:
    filepath = Path(filepath)
    with filepath.open("rb") as f:
        return pickle.load(f)  # nosec  # noqa: S301


def save_pickle_file(filepath, data):
    filepath = Path(filepath)
    with filepath.open("wb") as f:
        pickle.dump(data, f)
