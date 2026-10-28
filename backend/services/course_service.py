from neo4j import Session
from typing import List, Dict, Any, Optional

class CourseService:
    @staticmethod
    def get_all_courses(session: Session) -> List[Dict[str, Any]]:
        query = """
        MATCH (c:Course)
        OPTIONAL MATCH (cl:Class)-[:FOR_COURSE]->(c)
        RETURN c.course_code AS course_code,
               c.title AS title,
               coalesce(c.credits, 3) AS credits,
               coalesce(c.department, 'CSE') AS department,
               count(cl) AS active_sections
        ORDER BY c.course_code
        """
        records = session.run(query)
        courses = []
        for r in records:
            courses.append({
                "course_code": r["course_code"],
                "title": r["title"],
                "credits": r["credits"],
                "department": r["department"],
                "active_sections": r["active_sections"]
            })
        return courses

    @staticmethod
    def get_all_slots(session: Session) -> List[Dict[str, Any]]:
        query = """
        MATCH (s:Slot)
        OPTIONAL MATCH (cl:Class)-[:SCHEDULED_AT]->(s)
        RETURN s.slot_name AS slot_name,
               s.day AS day,
               s.start_time AS start_time,
               s.end_time AS end_time,
               count(cl) AS class_count
        ORDER BY s.day, s.start_time
        """
        records = session.run(query)
        slots = []
        for r in records:
            slots.append({
                "slot_name": r["slot_name"],
                "day": r["day"],
                "start_time": r["start_time"],
                "end_time": r["end_time"],
                "class_count": r["class_count"]
            })
        return slots

    @staticmethod
    def explore_classes(
        session: Session,
        slot_name: Optional[str] = None,
        faculty_name: Optional[str] = None,
        department: Optional[str] = None,
        search_query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Explores classes with real-time seat availability and filters.
        """
        where_clauses = []
        params = {}

        if slot_name and slot_name.strip():
            where_clauses.append("sl.slot_name = $slot_name")
            params["slot_name"] = slot_name.strip()

        if faculty_name and faculty_name.strip():
            where_clauses.append("toLower(f.name) CONTAINS toLower($faculty_name)")
            params["faculty_name"] = faculty_name.strip()

        if department and department.strip() and department.upper() != "ALL":
            where_clauses.append("(toLower(c.department) = toLower($department) OR toLower(f.department) = toLower($department) OR toLower(f.school) = toLower($department))")
            params["department"] = department.strip()

        if search_query and search_query.strip():
            where_clauses.append("(toLower(c.course_code) CONTAINS toLower($q) OR toLower(c.title) CONTAINS toLower($q) OR toLower(f.name) CONTAINS toLower($q) OR toLower(v.building) CONTAINS toLower($q))")
            params["q"] = search_query.strip()

        where_stmt = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        cypher = f"""
        MATCH (cl:Class)-[:FOR_COURSE]->(c:Course)
        MATCH (cl)-[:SCHEDULED_AT]->(sl:Slot)
        MATCH (cl)-[:HELD_IN]->(v:Venue)
        MATCH (cl)-[:TAUGHT_BY]->(f:Faculty)
        {where_stmt}
        OPTIONAL MATCH (s:Student)-[:REGISTERED_IN]->(cl)
        WITH cl, c, sl, v, f, count(s) AS registered_count
        RETURN cl.class_id AS class_id,
               c.course_code AS course_code,
               c.title AS course_title,
               coalesce(c.credits, 3) AS credits,
               coalesce(c.department, 'CSE') AS department,
               sl.slot_name AS slot_name,
               sl.day AS day,
               sl.start_time AS start_time,
               sl.end_time AS end_time,
               v.building + '-' + v.room_no AS venue,
               v.building AS building,
               v.room_no AS room_no,
               coalesce(v.capacity, 60) AS capacity,
               f.name AS faculty_name,
               coalesce(f.department, f.school, 'Faculty') AS faculty_dept,
               registered_count,
               (coalesce(v.capacity, 60) - registered_count) AS available_seats,
               (registered_count >= coalesce(v.capacity, 60)) AS is_full
        ORDER BY c.course_code, cl.class_id
        """
        records = session.run(cypher, **params)
        classes = []
        for r in records:
            classes.append({
                "class_id": r["class_id"],
                "course_code": r["course_code"],
                "course_title": r["course_title"],
                "credits": r["credits"],
                "department": r["department"],
                "slot_name": r["slot_name"],
                "day": r["day"],
                "start_time": r["start_time"],
                "end_time": r["end_time"],
                "venue": r["venue"],
                "building": r["building"],
                "room_no": r["room_no"],
                "capacity": r["capacity"],
                "faculty_name": r["faculty_name"],
                "faculty_dept": r["faculty_dept"],
                "registered_count": r["registered_count"],
                "available_seats": max(0, r["available_seats"]),
                "is_full": r["is_full"]
            })
        return classes
