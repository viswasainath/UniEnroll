from neo4j import Session
from typing import List, Dict, Any, Optional

class VenueService:
    @staticmethod
    def get_buildings(session: Session) -> List[str]:
        query = """
        MATCH (v:Venue)
        RETURN DISTINCT v.building AS building
        ORDER BY building
        """
        records = session.run(query)
        return [r["building"] for r in records if r["building"]]

    @staticmethod
    def get_overbooking_audit(session: Session) -> List[Dict[str, Any]]:
        query = """
        MATCH (v:Venue)<-[:HELD_IN]-(cl:Class)
        OPTIONAL MATCH (cl)<-[:REGISTERED_IN]-(s:Student)
        OPTIONAL MATCH (cl)-[:FOR_COURSE]->(c:Course)
        OPTIONAL MATCH (cl)-[:SCHEDULED_AT]->(sl:Slot)
        OPTIONAL MATCH (cl)-[:TAUGHT_BY]->(f:Faculty)
        WITH v, cl, c, sl, f, count(s) AS Registered_Students
        RETURN v.building + '-' + v.room_no AS Venue,
               v.building AS Building,
               v.room_no AS Room_No,
               cl.class_id AS Class,
               coalesce(c.course_code, 'N/A') AS Course_Code,
               coalesce(c.title, 'N/A') AS Course_Title,
               coalesce(sl.slot_name, 'N/A') AS Slot,
               coalesce(sl.day, '') AS Day,
               coalesce(f.name, 'TBA') AS Faculty,
               coalesce(v.capacity, 60) AS Max_Capacity,
               Registered_Students,
               (Registered_Students > coalesce(v.capacity, 60)) AS Is_Overbooked,
               round(toFloat(Registered_Students) / coalesce(v.capacity, 60) * 100, 1) AS Occupancy_Rate
        ORDER BY Is_Overbooked DESC, Occupancy_Rate DESC, Registered_Students DESC
        """
        records = session.run(query)
        audits = []
        for r in records:
            audits.append({
                "venue": r["Venue"],
                "building": r["Building"],
                "room_no": r["Room_No"],
                "class_id": r["Class"],
                "course_code": r["Course_Code"],
                "course_title": r["Course_Title"],
                "slot": r["Slot"],
                "day": r["Day"],
                "faculty": r["Faculty"],
                "max_capacity": r["Max_Capacity"],
                "registered_students": r["Registered_Students"],
                "is_overbooked": r["Is_Overbooked"],
                "occupancy_rate": r["Occupancy_Rate"]
            })
        return audits

    @staticmethod
    def find_empty_venues(session: Session, slot_name: str, building: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Empty Venue Finder (Smart Room Allocation):
        Filter by building and Slot to return all vacant rooms.
        """
        if building and building.strip() and building.upper() != "ALL":
            query = """
            MATCH (v:Venue {building: $building})
            WHERE NOT EXISTS {
                MATCH (v)<-[:HELD_IN]-(cl:Class)-[:SCHEDULED_AT]->(s:Slot {slot_name: $slot_name})
            }
            RETURN v.building AS Building,
                   v.room_no AS Room_No,
                   v.building + '-' + v.room_no AS Venue,
                   coalesce(v.capacity, 60) AS Capacity
            ORDER BY v.building, v.room_no
            """
            records = session.run(query, building=building.strip(), slot_name=slot_name.strip())
        else:
            query = """
            MATCH (v:Venue)
            WHERE NOT EXISTS {
                MATCH (v)<-[:HELD_IN]-(cl:Class)-[:SCHEDULED_AT]->(s:Slot {slot_name: $slot_name})
            }
            RETURN v.building AS Building,
                   v.room_no AS Room_No,
                   v.building + '-' + v.room_no AS Venue,
                   coalesce(v.capacity, 60) AS Capacity
            ORDER BY v.building, v.room_no
            """
            records = session.run(query, slot_name=slot_name.strip())

        empty_venues = []
        for r in records:
            empty_venues.append({
                "building": r["Building"],
                "room_no": r["Room_No"],
                "venue": r["Venue"],
                "capacity": r["Capacity"],
                "slot": slot_name
            })
        return empty_venues
