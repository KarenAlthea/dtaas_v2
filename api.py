from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel

from components import COMPONENTS
from template_builder import build_template_schema
from compiler import compile_twin
from kpi import compute_kpis
from simpy_runtime import run_flowline_sim

api_router = APIRouter()


class CasePayload(BaseModel):
    case: Dict[str, Any]


class InstancePayload(BaseModel):
    instance: Dict[str, Any]


@api_router.get("/status")
def status():
    return {"status": "ok", "service": "DTaaS v0.2"}


@api_router.get("/components")
def list_components():
    return [{"id": k, "name": v["name"]} for k, v in COMPONENTS.items()]


@api_router.post("/template-builder/schema")
def template_builder_schema(payload: CasePayload):
    return build_template_schema(payload.case)


@api_router.post("/generate-twin")
def generate_twin(payload: InstancePayload):
    twin = compile_twin(payload.instance)
    return {"twin": twin}


@api_router.post("/compute-kpi")
def compute_kpi(payload: InstancePayload):
    kpis = compute_kpis(payload.instance)
    twin = compile_twin(payload.instance)
    return {"kpis": kpis, "twin": twin}


@api_router.post("/simulate")
def simulate(payload: InstancePayload):
    result = run_flowline_sim(payload.instance)
    return {"result": result}
