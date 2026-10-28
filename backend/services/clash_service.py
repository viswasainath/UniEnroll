from neo4j import Session
from typing import List, Dict, Any

class ClashService:
    @staticmethod
    def validate_pre_registration(session: Session, reg_no: str, target_class_id: str) -> Dict[str, Any]:
        """
        Validates whether adding target_class_id for student reg_no produces a slot clash.
        """
        # Get target class info
        target_info = session.run("""
            MATCH (cl:Class {class_id: $target_class_id})
            OPTIONAL MATCH (cl)-[:FOR_COURSE]->(c:Course)
            OPTIONAL MATCH (cl)-[:SCHEDULED_AT]->(sl:Slot)
            RETURN cl.class_id AS class_id, c.course_code AS course_code, c.title AS course_title,
                   sl.slot_name AS slot_name, sl.day AS day, sl.start_time AS start_time, sl.end_time AS end_time
        """, target_class_id=target_class_id).single()

        if not target_info or not target_info["slot_name"]:
            return {
                "has_clash": False,
                "message": "Target class not found or has no scheduled slot."
            }

        target_slot = target_info["slot_name"]

        # Check existing slot registrations
        query = """
        MATCH (s:Student {reg_no: $reg_no})-[:REGISTERED_IN]->(cl1:Class)-[:SCHEDULED_AT]->(slot1:Slot)
        MATCH (target_cl:Class {class_id: $target_class_id})-[:SCHEDULED_AT]->(slot2:Slot)
        MATCH (cl1)-[:FOR_COURSE]->(c1:Course)
        MATCH (target_cl)-[:FOR_COURSE]->(c2:Course)
        WHERE slot1.slot_name = slot2.slot_name
        RETURN slot1.slot_name AS Clashing_Slot,
               slot1.day AS Day,
               slot1.start_time AS Start_Time,
               slot1.end_time AS End_Time,
               cl1.class_id AS Existing_Class,
               c1.course_code AS Existing_Course_Code,
               c1.title AS Existing_Course_Title,
               c2.course_code AS Target_Course_Code,
               c2.title AS Target_Course_Title
        """
        records = list(session.run(query, reg_no=reg_no, target_class_id=target_class_id))

        if records:
            r = records[0]
            return {
                "has_clash": True,
                "clashing_slot": r["Clashing_Slot"],
                "day": r["Day"],
                "start_time": r["Start_Time"],
                "end_time": r["End_Time"],
                "existing_class": r["Existing_Class"],
                "existing_course_code": r["Existing_Course_Code"],
                "existing_course_title": r["Existing_Course_Title"],
                "target_class": target_class_id,
                "target_course_code": r["Target_Course_Code"],
                "target_course_title": r["Target_Course_Title"],
                "message": f"Conflict Alert: Target Class {target_class_id} ({r['Target_Course_Code']}) conflicts on Slot {r['Clashing_Slot']} ({r['Day']} {r['Start_Time']}-{r['End_Time']}) with your currently enrolled Class {r['Existing_Class']} ({r['Existing_Course_Code']})."
            }

        return {
            "has_clash": False,
            "target_class": target_class_id,
            "target_slot": target_slot,
            "message": f"Clean! Slot {target_slot} has no conflicts with existing courses."
        }

    @staticmethod
    def get_global_clashes(session: Session) -> List[Dict[str, Any]]:
        """
        Global Clash Audit Dashboard (Admin View):
        Returns all students with clashing registrations across two classes.
        """
        query = """
        MATCH (s:Student)-[:REGISTERED_IN]->(cl1:Class)-[:SCHEDULED_AT]->(slot1:Slot),
              (s)-[:REGISTERED_IN]->(cl2:Class)-[:SCHEDULED_AT]->(slot2:Slot)
        WHERE cl1.class_id < cl2.class_id AND slot1.slot_name = slot2.slot_name
        MATCH (cl1)-[:FOR_COURSE]->(c1:Course)
        MATCH (cl2)-[:FOR_COURSE]->(c2:Course)
        OPTIONAL MATCH (cl1)-[:HELD_IN]->(v1:Venue)
        OPTIONAL MATCH (cl2)-[:HELD_IN]->(v2:Venue)
        OPTIONAL MATCH (cl1)-[:TAUGHT_BY]->(f1:Faculty)
        OPTIONAL MATCH (cl2)-[:TAUGHT_BY]->(f2:Faculty)
        RETURN s.name AS Student,
               s.reg_no AS Reg_No,
               coalesce(s.department, s.program, 'CSE') AS Department,
               slot1.slot_name AS Clashing_Slot,
               slot1.day AS Day,
               slot1.start_time AS Start_Time,
               slot1.end_time AS End_Time,
               cl1.class_id AS Class_1,
               c1.course_code AS Course_1_Code,
               c1.title AS Course_1_Title,
               coalesce(v1.building + '-' + v1.room_no, 'TBA') AS Venue_1,
               coalesce(f1.name, 'TBA') AS Faculty_1,
               cl2.class_id AS Class_2,
               c2.course_code AS Course_2_Code,
               c2.title AS Course_2_Title,
               coalesce(v2.building + '-' + v2.room_no, 'TBA') AS Venue_2,
               coalesce(f2.name, 'TBA') AS Faculty_2
        ORDER BY s.reg_no, slot1.slot_name
        """
        records = session.run(query)
        clashes = []
        for r in records:
            clashes.append({
                "student_name": r["Student"],
                "reg_no": r["Reg_No"],
                "department": r["Department"],
                "clashing_slot": r["Clashing_Slot"],
                "day": r["Day"],
                "timing": f"{r['Start_Time']} - {r['End_Time']}",
                "class_1": {
                    "class_id": r["Class_1"],
                    "course_code": r["Course_1_Code"],
                    "course_title": r["Course_1_Title"],
                    "venue": r["Venue_1"],
                    "faculty": r["Faculty_1"]
                },
                "class_2": {
                    "class_id": r["Class_2"],
                    "course_code": r["Course_2_Code"],
                    "course_title": r["Course_2_Title"],
                    "venue": r["Venue_2"],
                    "faculty": r["Faculty_2"]
                }
            })
        return clashes
