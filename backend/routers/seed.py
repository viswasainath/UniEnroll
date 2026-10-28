from fastapi import APIRouter, Depends
from neo4j import Session
from ..database import get_db_session, Neo4jManager
from ..services.seed_service import SeedService

router = APIRouter(prefix="/api/seed", tags=["Database Management"])

@router.get("/status")
def get_db_status():
    return Neo4jManager.check_connection()

@router.post("/reset-and-seed")
def reset_database(session: Session = Depends(get_db_session)):
    return SeedService.reset_and_seed(session)
