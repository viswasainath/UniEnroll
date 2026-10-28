from fastapi import APIRouter, Depends, Query
from neo4j import Session
from ..database import get_db_session
from ..services.clash_service import ClashService

router = APIRouter(prefix="/api/clashes", tags=["Clash Detection"])

@router.get("/validate")
def validate_registration(
    reg_no: str = Query(..., description="Student registration number"),
    target_class_id: str = Query(..., description="Target class ID to check for clashes"),
    session: Session = Depends(get_db_session)
):
    return ClashService.validate_pre_registration(session, reg_no, target_class_id)

@router.get("/global-audit")
def global_clash_audit(session: Session = Depends(get_db_session)):
    return ClashService.get_global_clashes(session)
