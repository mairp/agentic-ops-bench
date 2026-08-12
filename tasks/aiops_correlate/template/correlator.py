"""Alert correlation for a NOC event stream.

correlate(events) -> list of alerts.

events: dicts {"ts": int (seconds), "device": str, "msg": str}, possibly
unsorted. Sort by (ts, device, msg) first, then run three stages IN ORDER:

STAGE 1 — dedup. Per (device, msg), walk the events in order with an
ANCHORED window: an event joins the current group while
ts - first_ts_of_group <= 60, otherwise it starts a new group. Each group
becomes one alert {"ts": first ts, "device": ..., "msg": ..., "count": n}.

STAGE 2 — link flap. Link alerts are those with msg "LINK-UP" or
"LINK-DOWN". Per device, walk its link alerts in ts order with an anchored
300s window (joins while alert.ts - first.ts <= 300). A window holding >= 3
link alerts is REPLACED by the single alert {"ts": first ts, "device": ...,
"msg": "LINK-FLAP", "count": sum of the replaced counts}. Windows with 1-2
alerts keep their original alerts.

STAGE 3 — widespread. Per msg (excluding "LINK-FLAP"), walk the surviving
alerts in ts order with an anchored 120s window. If a window contains alerts
from >= 3 DISTINCT devices, ADD the alert {"ts": first ts of the window,
"device": "*", "msg": ..., "count": number of distinct devices}. The
individual alerts are KEPT.

Return all alerts sorted by (ts, device, msg).
"""


def correlate(events):
    raise NotImplementedError
