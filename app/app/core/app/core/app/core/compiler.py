import uuid
from typing import Any, Dict


def compile_twin(instance: Dict[str, Any]) -> Dict[str, Any]:
    """
    Turns an instance into a minimal internal twin representation (twin graph).
    This is NOT a full simulation model; it is a structured, versionable model.
    """
    line = instance.get("line", {})
    stations = instance.get("stations", [])
    buffers = instance.get("buffers", [])

    nodes = [{"id": "SRC", "type": "source"}]
    edges = []

    # add stations
    for s in stations:
        nodes.append(
            {
                "id": s["id"],
                "type": "station",
                "station_type": s.get("type"),
                "cycle_time_s": s.get("cycle_time_s"),
                "availability_pct": s.get("availability_pct"),
                "scrap_rate_pct": s.get("scrap_rate_pct", 0.0),
            }
        )

    nodes.append({"id": "SNK", "type": "sink"})

    # build edges with optional buffers
    prev = "SRC"
    for i, s in enumerate(stations):
        if i < len(buffers):
            b = buffers[i]
            buf_id = b["id"]
            nodes.append({"id": buf_id, "type": "buffer", "capacity": b.get("capacity", 0)})
            edges.append({"from": prev, "to": s["id"]})
            edges.append({"from": s["id"], "to": buf_id})
            prev = buf_id
        else:
            edges.append({"from": prev, "to": s["id"]})
            prev = s["id"]

    edges.append({"from": prev, "to": "SNK"})

    return {
        "twin_id": str(uuid.uuid4()),
        "line_name": line.get("line_name", "Unnamed"),
        "meta": {"schema": "twin_graph_v1"},
        "nodes": nodes,
        "edges": edges,
        "sim": instance.get("sim", {}),
    }
