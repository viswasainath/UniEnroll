from fastapi import APIRouter, Depends, Query
from neo4j import Session
from typing import Optional
from ..database import get_db_session
from ..services.venue_service import VenueService

router = APIRouter(prefix="/api/venues", tags=["Venues & Logistics"])

@router.get("/buildings")
def list_buildings(session: Session = Depends(get_db_session)):
    return VenueService.get_buildings(session)

@router.get("/overbooking-audit")
def overbooking_audit(session: Session = Depends(get_db_session)):
    return VenueService.get_overbooking_audit(session)

@router.get("/empty")
def find_empty_venues(
    slot_name: str = Query(..., description="Target slot name e.g. A1, B1"),
    building: Optional[str] = Query(None, description="Optional building filter e.g. AB1, SMV"),
    session: Session = Depends(get_db_session)
):
    return VenueService.find_empty_venues(session, slot_name=slot_name, building=building)
