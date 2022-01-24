def get_location(window, key=None, keyx=None, keyy=None, dx=0, dy=0):
    x, y = window.CurrentLocation()
    if key:
        x = window[key].Widget.winfo_rootx()
        y = window[key].Widget.winfo_rooty()
    else:
        if keyx:
            x = window[keyx].Widget.winfo_rootx()
        if keyy:
            y = window[keyy].Widget.winfo_rooty()
    return (x + dx, y + dy)
