import random
from typing import Any, Dict

import simpy


def run_flowline_sim(instance: Dict[str, Any]) -> Dict[str, Any]:
    """
    Minimal SimPy flow-line simulation:
    - Jobs arrive from a source (interarrival)
    - Go through N stations (single server)
    - Optional buffers between stations (Store with capacity)
    - Very simple availability + scrap behavior
    """
    horizon_s = float(instance["sim"]["horizon_s"])
    interarrival_s = float(instance["sim"]["interarrival_s"])

    stations = instance["stations"]
    buffers = instance.get("buffers", [])

    env = simpy.Environment()
    resources = {s["id"]: simpy.Resource(env, capacity=1) for s in stations}

    stores = []
    for b in buffers:
        cap = int(b.get("capacity", 0))
        # Store capacity must be >=1, use 1 for "no buffer but keep structure"
        stores.append(simpy.Store(env, capacity=max(1, cap)))

    started = 0
    completed_good = 0
    scrapped = 0

    def do_station(s, job_id):
        nonlocal scrapped
        ct = float(s["cycle_time_s"])
        avail = float(s["availability_pct"]) / 100.0
        scrap = float(s.get("scrap_rate_pct", 0.0)) / 100.0

        with resources[s["id"]].request() as req:
            yield req
            # downtime proxy: if unavailable, add extra delay
            if random.random() > avail:
                yield env.timeout(ct)
            yield env.timeout(ct)

        if random.random() < scrap:
            scrapped += 1
            return False
        return True

    def job(job_id):
        nonlocal completed_good, started
        started += 1

        for i, s in enumerate(stations):
            ok = yield env.process(do_station(s, job_id))
            if not ok:
                return

            # buffer between station i and i+1
            if i < len(stations) - 1 and i < len(stores):
                yield stores[i].put(job_id)
                _ = yield stores[i].get()

        completed_good += 1

    def source():
        job_id = 0
        while env.now < horizon_s:
            job_id += 1
            env.process(job(job_id))
            yield env.timeout(interarrival_s)

    env.process(source())
    env.run(until=horizon_s)

    throughput_pph = (completed_good / horizon_s) * 3600.0
    return {
        "horizon_s": horizon_s,
        "started_jobs": started,
        "completed_good": completed_good,
        "scrapped": scrapped,
        "throughput_pph_sim": round(throughput_pph, 2),
    }
