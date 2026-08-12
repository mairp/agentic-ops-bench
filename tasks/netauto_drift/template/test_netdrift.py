from netdrift.parser import parse_config
from netdrift.differ import plan

RUNNING = """\
hostname edge1
interface GigabitEthernet0/1
 ip address 10.0.0.1 255.255.255.0
 shutdown
interface GigabitEthernet0/2
 description peering
interface Loopback0
 ip address 1.1.1.1 255.255.255.255
"""

INTENDED = """\
hostname edge1
interface Gi0/1
 ip address 10.0.0.2 255.255.255.0
 description uplink
interface Gi0/2
 description peering
"""


def test_plan_full():
    p = plan(parse_config(RUNNING), parse_config(INTENDED))
    assert p == [
        "interface GigabitEthernet0/1",
        " no ip address 10.0.0.1 255.255.255.0",
        " no shutdown",
        " ip address 10.0.0.2 255.255.255.0",
        " description uplink",
        "default interface Loopback0",
    ]


def test_matching_iface_across_name_forms_is_silent():
    r = parse_config("interface GigabitEthernet0/2\n description peering\n")
    i = parse_config("interface Gi0/2\n description peering\n")
    assert plan(r, i) == []


def test_new_interface_is_all_adds():
    r = parse_config("hostname x\n")
    i = parse_config("interface Lo1\n ip address 2.2.2.2 255.255.255.255\n")
    assert plan(r, i) == ["interface Loopback1",
                          " ip address 2.2.2.2 255.255.255.255"]
