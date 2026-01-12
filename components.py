# Minimal component library: building blocks

COMPONENTS = {
    "source": {
        "name": "Source",
        "params": {
            "interarrival_s": {
                "type": "number",
                "minimum": 0.1,
                "default": 5,
                "title": "Interarrival time (s)",
            }
        },
    },
    "station": {
        "name": "Station",
        "params": {
            "type": {"type": "string", "enum": ["assembly", "welding"], "title": "Station type"},
            "cycle_time_s": {"type": "number", "minimum": 1, "maximum": 600, "title": "Cycle time (s)"},
            "availability_pct": {"type": "number", "minimum": 50, "maximum": 99.9, "title": "Availability (%)"},
            "scrap_rate_pct": {"type": "number", "minimum": 0, "maximum": 20, "default": 0.0, "title": "Scrap (%)"},
        },
    },
    "buffer": {
        "name": "Buffer",
        "params": {
            "capacity": {"type": "integer", "minimum": 0, "maximum": 500, "default": 10, "title": "Capacity (pcs)"}
        },
    },
    "sink": {"name": "Sink", "params": {}},
}
