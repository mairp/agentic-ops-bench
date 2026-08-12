import pytest
from netacl import cidr_to_wildcard, render_rule, compile_acl, find_shadowed


def R(action="permit", proto="tcp", src="0.0.0.0/0", dst="0.0.0.0/0", dst_port=None):
    return {"action": action, "proto": proto, "src": src, "dst": dst,
            "dst_port": dst_port}


def test_wildcards():
    assert cidr_to_wildcard("10.0.0.0/24") == ("10.0.0.0", "0.0.0.255")
    assert cidr_to_wildcard("10.0.0.0/25") == ("10.0.0.0", "0.0.0.127")
    assert cidr_to_wildcard("172.16.0.0/12") == ("172.16.0.0", "0.15.255.255")


def test_render_forms():
    assert render_rule(R(proto="tcp", src="10.0.0.0/24", dst_port=443)) == \
        "permit tcp 10.0.0.0 0.0.0.255 any eq 443"
    assert render_rule(R(action="deny", proto="udp", dst="192.168.1.5/32",
                         dst_port=(1000, 2000))) == \
        "deny udp any host 192.168.1.5 range 1000 2000"
    assert render_rule(R(proto="ip", src="172.16.0.0/12", dst="10.1.0.0/16")) == \
        "permit ip 172.16.0.0 0.15.255.255 10.1.0.0 0.0.255.255"


def test_port_on_ip_rejected():
    with pytest.raises(ValueError):
        render_rule(R(proto="ip", dst_port=80))


def test_compile():
    rules = [R(proto="tcp", src="10.0.0.0/24", dst_port=443),
             R(action="deny", proto="udp", dst="192.168.1.5/32",
               dst_port=(1000, 2000))]
    assert compile_acl("EDGE", rules) == [
        "ip access-list extended EDGE",
        " 10 permit tcp 10.0.0.0 0.0.0.255 any eq 443",
        " 20 deny udp any host 192.168.1.5 range 1000 2000",
        " 30 deny ip any any",
    ]


def test_shadow_prefix_and_port():
    rules = [R(proto="tcp", src="10.0.0.0/8"),
             R(action="deny", proto="tcp", src="10.1.0.0/16", dst_port=80),
             R(proto="tcp", src="11.0.0.0/8", dst_port=80)]
    assert find_shadowed(rules) == [1]


def test_shadow_proto_ip_covers_all():
    rules = [R(proto="ip"), R(proto="tcp", dst_port=22)]
    assert find_shadowed(rules) == [1]


def test_shadow_port_range_superset_and_miss():
    rules = [R(proto="tcp", dst_port=(0, 1024)),
             R(proto="tcp", dst_port=80),
             R(proto="tcp", dst_port=2000)]
    assert find_shadowed(rules) == [1]
