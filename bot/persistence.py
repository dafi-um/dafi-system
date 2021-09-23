import shelve
from typing import (
    Any,
    ItemsView,
)

import schedule


_shelf = None


def load() -> None:
    """Loads the saved data to the memory.
    """
    global _shelf

    if _shelf is not None:
        # Shelf already loaded
        return

    _shelf = shelve.open('botstorage', writeback=True)

    schedule.every(5).minutes.do(_shelf.sync)


def close() -> None:
    """Saves the data to the disk and closes the file.
    """
    global _shelf
    assert _shelf is not None

    _shelf.close()


def sync() -> None:
    """Saves the data to the disk.
    """
    global _shelf
    assert _shelf is not None

    _shelf.sync()


def flush() -> None:
    """Flushes the persistent data.
    """
    global _shelf
    assert _shelf is not None

    for key in _shelf.keys():
        del _shelf[key]

    _shelf.sync()


def get_all() -> ItemsView[str, Any]:
    """Gets all the items in the persistent data dictionary.
    """
    global _shelf
    assert _shelf is not None
    return _shelf.items()


def get_item(key: str, default: Any) -> Any:
    """Gets an item from the persistent data dictionary.

    If it does not exist, creates it.
    """
    global _shelf
    assert _shelf is not None

    if key not in _shelf:
        _shelf[key] = default

    return _shelf[key]


def set_item(key: str, value: Any) -> None:
    """Updates an item value in the persistent data dictionary.
    """
    global _shelf
    assert _shelf is not None
    _shelf[key] = value
