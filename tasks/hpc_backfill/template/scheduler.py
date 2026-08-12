"""EASY-backfill batch scheduler (conservative variant).

schedule(jobs, total_nodes) -> {job_id: start_time}

jobs: dicts {"id": str, "submit": int, "nodes": int, "walltime": int}.
A job occupies its nodes for [start, start + walltime). Any job with
nodes > total_nodes raises ValueError before the simulation starts.

The pending queue is ordered by (submit, id). The simulation is
event-driven: decision points are every job-submit time and every
running-job end time, processed in increasing order. At each decision
point t:

  1. Nodes of jobs ending at or before t are free.
  2. While the queue head (earliest (submit, id) with submit <= t) fits in
     the free nodes, start it at t.
  3. If the head is blocked, compute its RESERVATION t_r: the earliest time
     >= t with enough free nodes for it, assuming running jobs release
     their nodes at their end times and nothing else starts.
  4. Backfill: scan the remaining pending jobs (submit <= t) in queue
     order; start any job that fits in the CURRENTLY free nodes AND
     finishes by the reservation (t + walltime <= t_r). Update the free
     count as backfills start. The head must never be delayed past t_r.
"""


def schedule(jobs, total_nodes):
    raise NotImplementedError
