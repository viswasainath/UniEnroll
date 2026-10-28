from neo4j import Session
from typing import List, Dict, Any, Optional

class FacultyService:
    @staticmethod
    def get_all_faculty(session: Session) -> List[Dict[str, Any]]:
        query = """
        MATCH (f:Faculty)
        OPTIONAL MATCH (f)<-[:TAUGHT_BY]-(cl:Class)
        OPTIONAL MATCH (cl)<-[:REGISTERED_IN]-(s:Student)
        RETURN coalesce(f.faculty_id, f.emp_id, f.name) AS faculty_id,
               f.name AS name,
               coalesce(f.designation, 'Professor') AS designation,
               coalesce(f.department, f.school, 'Faculty') AS department,
               count(DISTINCT cl) AS classes_count,
               count(s) AS total_students
        ORDER BY f.name
        """
        records = session.run(query)
        faculty_list = []
        for r in records:
            faculty_list.append({
                "faculty_id": r["faculty_id"],
                "name": r["name"],
                "designation": r["designation"],
                "department": r["department"],
                "classes_count": r["classes_count"],
                "total_students": r["total_students"]
            })
        return faculty_list

    @staticmethod
    def get_faculty_schedule(session: Session, faculty_name: str) -> Dict[str, Any]:
        query = """
        MATCH (f:Faculty)
        WHERE toLower(f.name) = toLower($faculty_name) OR f.faculty_id = $faculty_name OR f.emp_id = $faculty_name
        OPTIONAL MATCH (f)<-[:TAUGHT_BY]-(cl:Class)
        OPTIONAL MATCH (cl)-[:SCHEDULED_AT]->(s:Slot)
        OPTIONAL MATCH (cl)-[:HELD_IN]->(v:Venue)
        OPTIONAL MATCH (cl)-[:FOR_COURSE]->(c:Course)
        OPTIONAL MATCH (cl)<-[:REGISTERED_IN]-(st:Student)
        WITH f, cl, s, v, c, count(st) AS registered_students
        RETURN f.name AS Faculty,
               coalesce(f.faculty_id, f.emp_id, 'N/A') AS Faculty_ID,
               coalesce(f.designation, 'Professor') AS Designation,
               coalesce(f.department, f.school, 'Faculty') AS Department,
               cl.class_id AS Class,
               coalesce(c.course_code, 'N/A') AS Course_Code,
               coalesce(c.title, 'N/A') AS Course_Title,
               coalesce(c.credits, 3) AS Credits,
               coalesce(s.slot_name, 'N/A') AS Slot,
               coalesce(s.day, 'MON') AS Day,
               coalesce(s.start_time, '08:00') AS Start_Time,
               coalesce(s.end_time, '08:50') AS End_Time,
               coalesce(v.building + '-' + v.room_no, 'TBA') AS Venue,
               coalesce(v.capacity, 60) AS Venue_Capacity,
               registered_students
        ORDER BY s.day, s.start_time
        """
        records = list(session.run(query, faculty_name=faculty_name))
        if not records:
            return {"faculty_name": faculty_name, "classes": [], "slot_map": {}, "summary": {}}

        faculty_info = {
            "name": records[0]["Faculty"],
            "faculty_id": records[0]["Faculty_ID"],
            "designation": records[0]["Designation"],
            "department": records[0]["Department"]
        }

        classes = []
        slot_map = {}
        total_students = 0

        for r in records:
            if not r["Class"]:
                continue
            item = {
                "class_id": r["Class"],
                "course_code": r["Course_Code"],
                "course_title": r["Course_Title"],
                "credits": r["Credits"],
                "slot": r["Slot"],
                "day": r["Day"],
                "start_time": r["Start_Time"],
                "end_time": r["End_Time"],
                "venue": r["Venue"],
                "venue_capacity": r["Venue_Capacity"],
                "registered_students": r["registered_students"]
            }
            classes.append(item)
            if item["slot"] not in slot_map:
                slot_map[item["slot"]] = item
            total_students += r["registered_students"]

        return {
            "faculty": faculty_info,
            "classes": classes,
            "slot_map": slot_map,
            "summary": {
                "total_classes": len(classes),
                "total_students": total_students,
                "weekly_teaching_hours": len(classes) * 1.0
            }
        }
