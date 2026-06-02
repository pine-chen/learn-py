from fastapi import APIRouter

from app.schemas.requirement import RequirementParseRequest
from app.services.requirement_parser import parse_requirement

router = APIRouter(
    prefix="/requirements",
    tags=["requirements"],
)

@router.post("/parse")
def parse_requirement_api(request: RequirementParseRequest,):
    return parse_requirement(request.content)