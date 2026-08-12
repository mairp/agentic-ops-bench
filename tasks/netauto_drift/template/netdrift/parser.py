"""Parse a minimal IOS-style config into sections."""

_LONG = {"Gi": "GigabitEthernet", "Te": "TenGigabitEthernet",
         "Fa": "FastEthernet", "Lo": "Loopback"}


def canon(name):
    """Canonical (long-form) interface name: 'Gi0/1' -> 'GigabitEthernet0/1'.
    Names already in long form pass through unchanged."""
    for full in _LONG.values():
        if name.startswith(full):
            return name
    for short, full in _LONG.items():
        if name.startswith(short):
            return full + name[len(short):]
    return name


def parse_config(text):
    """-> {"global": [lines], "interfaces": {name_as_written: [child lines]}}.

    A line starting with "interface " opens a block; indented lines below it
    are its children (stored stripped, in order). Blank lines and "!" end the
    current block. Interface names are stored AS WRITTEN — different configs
    may use short or long forms for the same interface, so compare names
    across configs with canon()."""
    out = {"global": [], "interfaces": {}}
    cur = None
    for raw in text.splitlines():
        s = raw.strip()
        if not s or s == "!":
            cur = None
            continue
        if raw[0] in " \t":
            if cur is not None:
                out["interfaces"][cur].append(s)
            else:
                out["global"].append(s)
            continue
        if s.startswith("interface "):
            cur = s.split(None, 1)[1]
            out["interfaces"].setdefault(cur, [])
        else:
            cur = None
            out["global"].append(s)
    return out
