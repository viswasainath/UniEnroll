from fastapi import APIRouter, Depends, HTTPException
from neo4j import Session
from pydantic import BaseModel
from typing import Optional
from ..database import get_db_session
from ..services.student_service import StudentService

router = APIRouter(prefix="/api/students", tags=["Students"])

class RegisterClassRequest(BaseModel):
    class_id: str

@router.get("")
def list_students(session: Session = Depends(get_db_session)):
    return StudentService.get_all_students(session)

@router.get("/{reg_no}")
def get_student(reg_no: str, session: Session = Depends(get_db_session)):
    student = StudentService.get_student_profile(session, reg_no)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student {reg_no} not found")
    return student

@router.get("/{reg_no}/timetable")
def get_student_timetable(reg_no: str, session: Session = Depends(get_db_session)):
    return StudentService.get_student_timetable(session, reg_no)

@router.get("/{reg_no}/graph")
def get_student_graph(reg_no: str, session: Session = Depends(get_db_session)):
    return StudentService.get_student_graph_data(session, reg_no)

@router.post("/{reg_no}/register")
def register_student_class(
    reg_no: str,
    payload: RegisterClassRequest,
    session: Session = Depends(get_db_session)
):
    result = StudentService.register_class(session, reg_no, payload.class_id)
    if not result.get("success"):
        return {"success": False, "error": result}
    return result

@router.delete("/{reg_no}/classes/{class_id}")
def drop_student_class(
    reg_no: str,
    class_id: str,
    session: Session = Depends(get_db_session)
):
    result = StudentService.drop_class(session, reg_no, class_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result
