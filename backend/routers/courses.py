from fastapi import APIRouter, Depends, Query
from neo4j import Session
from typing import Optional
from ..database import get_db_session
from ..services.course_service import CourseService

router = APIRouter(prefix="/api/courses", tags=["Courses"])

@router.get("")
def list_courses(session: Session = Depends(get_db_session)):
    return CourseService.get_all_courses(session)

@router.get("/slots")
def list_slots(session: Session = Depends(get_db_session)):
    return CourseService.get_all_slots(session)

@router.get("/explore")
def explore_classes(
    slot_name: Optional[str] = Query(None, description="Filter by slot, e.g. A1, B1"),
    faculty_name: Optional[str] = Query(None, description="Filter by faculty name"),
    department: Optional[str] = Query(None, description="Filter by department/school, e.g. SCOPE, SAS"),
    q: Optional[str] = Query(None, description="General search query"),
    session: Session = Depends(get_db_session)
):
    return CourseService.explore_classes(
        session=session,
        slot_name=slot_name,
        faculty_name=faculty_name,
        department=department,
        search_query=q
    )
