"""Compute a CLI change plan taking the `running` config to the `intended` one.

plan(running, intended) -> list of commands. Contract (encoded by the tests):

  * Interface names must be COMPARED CANONICALLY (running may say
    "GigabitEthernet0/1" where intended says "Gi0/1" — same interface), and
    every emitted command uses the canonical long-form name.
  * Intended interfaces are visited in intended order. For each changed
    block: emit "interface <canonical>", then the REMOVALS first
    ("no <line>", in running order), then the additions (in intended order).
  * Blocks with no changes emit nothing.
  * Interfaces present only in running are cleaned afterwards with
    "default interface <canonical>", in running order.
"""


def plan(running, intended):
    cmds = []
    run_if = running["interfaces"]
    int_if = intended["interfaces"]
    for name, want in int_if.items():
        have = run_if.get(name, [])
        adds = [l for l in want if l not in have]
        removes = [l for l in have if l not in want]
        if adds or removes:
            cmds.append("interface %s" % name)
            for l in adds:
                cmds.append(" %s" % l)
            for l in removes:
                cmds.append(" no %s" % l)
    for name in run_if:
        if name not in int_if:
            cmds.append("default interface %s" % name)
    return cmds
