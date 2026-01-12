from app.core.components import COMPONENTS


def build_template_schema(case: dict) -> dict:
    """
    Builds JSON Schema for an instance based on a high-level "case".

    case example:
    {
      "num_stations": 3,
      "buffer_between": true
    }
    """
    num_stations = int(case.get("num_stations", 1))
    num_stations = max(1, min(num_stations, 10))

    buffer_between = bool(case.get("buffer_between", True))
    n_buffers = (num_stations - 1) if (buffer_between and num_stations > 1) else 0

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "required": ["line", "stations", "buffers", "sim"],
        "properties": {
            "line": {
                "type": "object",
                "required": ["line_name"],
                "properties": {"line_name": {"type": "string", "minLength": 2, "title": "Line name"}},
            },
            "stations": {
                "type": "array",
                "minItems": num_stations,
                "maxItems": num_stations,
                "items": {
                    "type": "object",
                    "required": ["id", "type", "cycle_time_s", "availability_pct"],
                    "properties": {"id": {"type": "string", "title": "Station ID"}, **COMPONENTS["station"]["params"]},
                },
            },
            "buffers": {
                "type": "array",
                "minItems": n_buffers,
                "maxItems": n_buffers,
                "items": {
                    "type": "object",
                    "required": ["id", "capacity"],
                    "properties": {"id": {"type": "string", "title": "Buffer ID"}, **COMPONENTS["buffer"]["params"]},
                },
            },
            "sim": {
                "type": "object",
                "required": ["horizon_s", "interarrival_s"],
                "properties": {
                    "horizon_s": {
                        "type": "number",
                        "minimum": 10,
                        "default": 3600,
                        "title": "Simulation horizon (s)",
                    },
                    "interarrival_s": COMPONENTS["source"]["params"]["interarrival_s"],
                },
            },
        },
    }

    return schema
