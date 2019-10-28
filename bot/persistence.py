import shelve

_shelf = None

def load():
    '''Loads the saved data to the memory'''

    global _shelf
    _shelf = shelve.open('botstorage', writeback=True)

def close():
    '''Saves the data to the disk and closes the file'''

    global _shelf
    _shelf.close()

def sync():
    '''Saves the data to the disk'''

    global _shelf
    _shelf.sync()

def flush():
    '''Flushes the persistent data'''

    global _shelf

    for key in _shelf.keys():
        del _shelf[key]

    _shelf.sync()

def get_all():
    '''Gets all the items in the persistent data dictionary'''

    global _shelf
    return _shelf.items()

def get_item(key, default):
    '''
    Gets an item from the persistent data dictionary.
    If it does not exist, creates it.
    '''

    global _shelf

    if key not in _shelf:
        _shelf[key] = default

    return _shelf[key]

def set_item(key, value):
    '''Updates an item value in the persistent data dictionary'''

    global _shelf
    _shelf[key] = value
