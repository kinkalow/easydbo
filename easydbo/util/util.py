def flat(li2d, unique=False):
    li = [li0d for li1d in li2d for li0d in li1d]
    if unique:
        return list(set(li))
    return li
