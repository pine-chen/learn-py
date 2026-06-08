from fastapi import APIRouter

from app.schemas.plan import PlanGenerateResponse, PlanGenerateRequest
from app.services.plan_generator import generate_plan

router = APIRouter(
    prefix="/plans",
    tags=["plans"],
)

@router.post("/generate", response_model=PlanGenerateResponse)
def generate_plan_api(request: PlanGenerateRequest):
    return generate_plan(request.query, request.limit)
