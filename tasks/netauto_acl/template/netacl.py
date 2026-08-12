"""Intent -> Cisco-style extended ACL compiler.

A rule is a dict:
    {"action": "permit"|"deny", "proto": "ip"|"tcp"|"udp",
     "src": <CIDR str>, "dst": <CIDR str>,
     "dst_port": None | int | (lo, hi)}

Address rendering:
    "0.0.0.0/0"       -> "any"
    a /32 prefix      -> "host <ip>"
    anything else     -> "<network> <wildcard>"   (wildcard = inverted mask)

Port clause (tcp/udp only; dst_port on proto "ip" -> ValueError):
    int       -> "eq <n>"
    (lo, hi)  -> "range <lo> <hi>"
    None      -> no clause

compile_acl(name, rules) returns the ACL as a list of lines:
    "ip access-list extended <name>", then one line per rule
    " <seq> <rendered rule>" with seq = 10, 20, 30, ..., then a final
    implicit " <seq> deny ip any any" at the next sequence number.

find_shadowed(rules) returns the ascending indices j of rules fully shadowed
by ANY earlier rule i (i < j): every packet j could match is already matched
by i. That requires ALL of: proto_i covers proto_j ("ip" covers everything,
otherwise they must be equal); src_i prefix contains src_j; dst_i contains
dst_j; and i's destination-port set contains j's (None = all ports, int =
that one port, (lo, hi) = the inclusive range). Actions are irrelevant to
shadowing. Each shadowed index appears once.
"""


def cidr_to_wildcard(cidr):
    """-> (network, wildcard) dotted strings, e.g. "10.0.0.0/24" ->
    ("10.0.0.0", "0.0.0.255")."""
    raise NotImplementedError


def render_rule(rule):
    """-> the rule as one string, e.g.
    "permit tcp 10.0.0.0 0.0.0.255 any eq 443" (no sequence number)."""
    raise NotImplementedError


def compile_acl(name, rules):
    """-> list of ACL lines incl. header and implicit deny (see module doc)."""
    raise NotImplementedError


def find_shadowed(rules):
    """-> ascending list of indices of fully-shadowed rules (see module doc)."""
    raise NotImplementedError
