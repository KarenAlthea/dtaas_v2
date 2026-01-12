from typing import Any, Dict


def compute_kpis(instance: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simple KPI estimation (not simulation):
    bottleneck-based throughput (capacity) with availability and scrap.
    """
    stations = instance.get("stations", [])
    if not stations:
        return {"error": "no stations"}

    capacities_pph = []
    for s in stations:
        ct = float(s["cycle_time_s"])
        avail = float(s["availability_pct"]) / 100.0
        scrap = float(s.get("scrap_rate_pct", 0.0)) / 100.0
        cap = (3600.0 / ct) * avail * (1.0 - scrap)
        capacities_pph.append((s["id"], cap))

    bottleneck_id, bottleneck_cap = min(capacities_pph, key=lambda x: x[1])

    target = instance.get("line", {}).get("target_throughput_pph")
    return {
        "bottleneck": bottleneck_id,
        "throughput_pph_est": round(bottleneck_cap, 2),
        "target_throughput_pph": target,
        "stations_capacity_pph": [{"id": sid, "cap": round(cap, 2)} for sid, cap in capacities_pph],
    }
