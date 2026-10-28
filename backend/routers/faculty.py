from fastapi import APIRouter, Depends
from neo4j import Session
from ..database import get_db_session
from ..services.faculty_service import FacultyService

router = APIRouter(prefix="/api/faculty", tags=["Faculty"])

@router.get("")
def list_faculty(session: Session = Depends(get_db_session)):
    return FacultyService.get_all_faculty(session)

@router.get("/{faculty_name}/schedule")
def get_faculty_schedule(faculty_name: str, session: Session = Depends(get_db_session)):
    return FacultyService.get_faculty_schedule(session, faculty_name)
