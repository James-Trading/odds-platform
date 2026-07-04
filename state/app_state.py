dirty = False


def mark_dirty():

    global dirty

    dirty = True


def mark_clean():

    global dirty

    dirty = False


def is_dirty():

    return dirty